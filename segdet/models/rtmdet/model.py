from typing import List, Tuple, Union
from torch import Tensor

from mmdet.registry import MODELS
from mmdet.structures import SampleList
from mmdet.utils import ConfigType, OptConfigType, OptMultiConfig
from mmdet.models.detectors.base import BaseDetector

from .head import RTMDetHead
from .neck import RTMNeck


class Model(BaseDetector):
    def __init__(
        self,
        backbone: ConfigType,
        neck: OptConfigType,
        bbox_head: OptConfigType,
        train_cfg: OptConfigType = None,
        test_cfg: OptConfigType = None,
        data_preprocessor: OptConfigType = None,
        init_cfg: OptMultiConfig = None,
    ) -> None:
        super().__init__(
            data_preprocessor=MODELS.build(data_preprocessor), init_cfg=init_cfg
        )
        self.backbone = MODELS.build(backbone)
        neck.pop("type")
        self.neck = RTMNeck(**neck)
        bbox_head.pop("type")
        self.bbox_head = RTMDetHead(**bbox_head, train_cfg=train_cfg, test_cfg=test_cfg)
        self.train_cfg = train_cfg
        self.test_cfg = test_cfg

    def loss(
        self, batch_inputs: Tensor, batch_data_samples: SampleList
    ) -> Union[dict, list]:
        print('yolo')
        x = self.extract_feat(batch_inputs)
        return self.bbox_head.loss(x, batch_data_samples)

    def predict(
        self, batch_inputs: Tensor, batch_data_samples: SampleList, rescale: bool = True
    ) -> SampleList:
        x = self.extract_feat(batch_inputs)
        results_list = self.bbox_head.predict(x, batch_data_samples, rescale=rescale)
        return self.add_pred_to_datasample(batch_data_samples, results_list)

    def _forward(self, batch_inputs: Tensor, *args, **kwargs) -> Tuple[List[Tensor]]:
        x = self.extract_feat(batch_inputs)
        return self.bbox_head(x)

    def extract_feat(self, batch_inputs: Tensor) -> Tuple[Tensor]:
        x = self.backbone(batch_inputs)
        return self.neck(x)

    def _load_from_state_dict(
        self,
        state_dict: dict,
        prefix: str,
        local_metadata: dict,
        strict: bool,
        missing_keys: Union[List[str], str],
        unexpected_keys: Union[List[str], str],
        error_msgs: Union[List[str], str],
    ) -> None:
        bbox_head_prefix = prefix + ".bbox_head" if prefix else "bbox_head"
        bbox_head_keys = [
            k for k in state_dict.keys() if k.startswith(bbox_head_prefix)
        ]
        rpn_head_prefix = prefix + ".rpn_head" if prefix else "rpn_head"
        rpn_head_keys = [k for k in state_dict.keys() if k.startswith(rpn_head_prefix)]
        if len(bbox_head_keys) == 0 and len(rpn_head_keys) != 0:
            for rpn_head_key in rpn_head_keys:
                bbox_head_key = bbox_head_prefix + rpn_head_key[len(rpn_head_prefix) :]
                state_dict[bbox_head_key] = state_dict.pop(rpn_head_key)
        super()._load_from_state_dict(
            state_dict,
            prefix,
            local_metadata,
            strict,
            missing_keys,
            unexpected_keys,
            error_msgs,
        )
