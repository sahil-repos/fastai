# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/74_callback.azureml.ipynb (unless otherwise specified).

__all__ = ['AzureMLCallback']

# Cell
from ..basics import *
from ..learner import Callback

# Cell
from azureml.core.run import Run

# Cell
class AzureMLCallback(Callback):
    "Log losses, metrics, model architecture summary to AzureML"
    order = Recorder.order+1

    def __init__(self, azurerun=None):
        if azurerun:
            self.azurerun = azurerun
        else:
            self.azurerun = Run.get_context()

    def before_fit(self):
        self.azurerun.log("n_epoch", self.learn.n_epoch)
        self.azurerun.log("model_class", str(type(self.learn.model)))

        try:
            summary_file = Path("outputs") / 'model_summary.txt'
            with summary_file.open("w") as f:
                f.write(repr(self.learn.model))
        except:
            print('Did not log model summary. Check if your model is PyTorch model.')

    def after_batch(self):
        # log loss and opt.hypers
        if self.learn.training:
            self.azurerun.log('batch__loss', self.learn.loss.item())
            self.azurerun.log('batch__train_iter', self.learn.train_iter)
            for i, h in enumerate(self.learn.opt.hypers):
                for k, v in h.items():
                    self.azurerun.log(f'batch__opt.hypers.{k}', v)

    def after_epoch(self):
        # log metrics
        for n, v in zip(self.learn.recorder.metric_names, self.learn.recorder.log):
            if n not in ['epoch', 'time']:
                self.azurerun.log(f'epoch__{n}', v)
            if n == 'time':
                # split elapsed time string, then convert into 'seconds' to log
                m, s = str(v).split(':')
                elapsed = int(m)*60 + int(s)
                self.azurerun.log(f'epoch__{n}', elapsed)