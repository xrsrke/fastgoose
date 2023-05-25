# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/05_optimizer.zero.ipynb.

# %% auto 0
__all__ = ['ZeRO']

# %% ../../nbs/05_optimizer.zero.ipynb 4
import torch
from torch import nn
from torch.optim import Optimizer, SGD

from ..mpu.parallel import ParallelState

# %% ../../nbs/05_optimizer.zero.ipynb 5
class ZeRO(Optimizer):
    def __init__(
        self,
        params,
        optim: Optimizer,
        parallel_state: ParallelState,
        defaults: dict = dict()
    ):
        super().__init__(params, defaults=defaults)
        self.optim = optim
        self.parallel_state = parallel_state
        
        self._init_local_optimizer()
    
    def _init_local_optimizer(self):
        rank = self.parallel_state.rank
        params_per_rank = self.param_to_ranks()
        param_of_current_rank = params_per_rank[rank]
        self.local_optim = self.optim(param_of_current_rank, **self.defaults)
    
    def param_to_ranks(self):
        for param_group in self.param_groups:
            params_per_rank = self._partrition_paramaters_per_rank(param_group['params'])
            return params_per_rank
    
    def _partrition_paramaters_per_rank(self, param_list):
        numel_per_rank = [0 for _ in range(self.world_size)]
        param_per_rank = [[] for _ in range(self.world_size)]
        sorted_params = sorted(param_list, key=lambda x: x.numel(), reverse=True)
        
        for param in sorted_params:
            rank = numel_per_rank.index(min(numel_per_rank))
            numel_per_rank[rank] += param.numel()
            param_per_rank[rank].append(param)
        
        return param_per_rank
