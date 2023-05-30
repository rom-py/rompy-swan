import logging

from rompy.core import BaseConfig, BaseModel

from .config import SwanConfig

logger = logging.getLogger(__name__)


class SwanModel(BaseModel):
    config: SwanConfig | BaseConfig = {}
    model: str = "SWAN"
    template: str = "/source/rompy/rompy/templates/swan"

    # @property
    # def subnests(self):
    #     """Process subnests for SWAN
    #
    #     Just a proposal for now. Provides an elegant way of initilising subnests
    #     """
    #     ii = 1
    #     subnests = []
    #     for config in self.config.subnests:
    #         self.reinit(
    #             instance=self, run_id=f"{self.run_id}_subnest{ii}", config=config
    #         )
    #         ii += 1
    #     return subnests

    @classmethod
    def reinit(cls, instance, run_id, **kwargs):
        """Re-initialise a model with the same configuration

        Parameters
        ----------
        run_id : str
            run_id of the previous run
        **kwargs
            Any additional keyword arguments to pass to the model initialisation

        Returns
        -------
        SwanModel
            A new model instance
        """
        kwg = instance.dict()
        kwg.pop("run_id")
        kwg.update(kwargs)
        model = cls(run_id=run_id, **kwg)
        return model

    # def generate(self):
    #     """Generate SWAN input files"""
    #     super().generate()
    #     for nest in self.subnests:
    #         nest.generate()
