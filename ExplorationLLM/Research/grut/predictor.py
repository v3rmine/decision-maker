from simpletransformers.seq2seq import Seq2SeqModel, Seq2SeqArgs
import torch
from simpletransformers.t5 import T5Model, T5Args

class Predictor:
    def __init__(self, model_name = 'bart', model_dir = 'outputs/best_model', num_beans = 1, return_sequences = 1, use_cuda = False):
        

        self.encoder_decoder_name = model_dir
        self.use_cuda = use_cuda

        cuda_available = torch.cuda.is_available() and self.use_cuda
        print('GPU available: ' + str(cuda_available))
        
        # if model_name == 'mt5':
        #     self.model_args = T5Args()
        #     self.model_args.num_beams = num_beans
        #     self.model_args.num_return_sequences = return_sequences

        #     self.model = T5Model(
        #         model_type="mt5",
        #         model_name=self.encoder_decoder_name,
        #         args=self.model_args,
        #         use_cuda=cuda_available
        #     )
        # elif model_name == 'bart':
        self.model_args = Seq2SeqArgs()
        self.model_args.num_beams = num_beans
        self.model_args.num_return_sequences = return_sequences

        self.model = Seq2SeqModel(
            encoder_decoder_type="bart",
            encoder_decoder_name=self.encoder_decoder_name,
            args=self.model_args,
            use_cuda=cuda_available
        )
        # else:
        #     print("ERROR")
        #     print("Only bart or mt5 models supported for now!")


    def predict(self, task, input):

        if not isinstance(input, list):
            input = [task + ": " + input]
        else:
            input = [task + ": " + x for x in input]
            
        return self.model.predict(input)

