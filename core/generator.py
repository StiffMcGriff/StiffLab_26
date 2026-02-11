from diffusers import StableDiffusionPipeline
import torch

class MusicGenerator:
    def __init__(self):
        self.model_id = "riffusion/riffusion-v1"
        self.pipe = StableDiffusionPipeline.from_pretrained(
            self.model_id, 
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        self.pipe = self.pipe.to("cuda" if torch.cuda.is_available() else "cpu")

    def generate(self, prompt):
        # Generate spectrogram
        output = self.pipe(prompt).images[0]
        # Convert spectrogram to audio (requires inverse STFT library like librosa or spec_to_audio)
        # Note: Riffusion usually includes a vocoder or Griffin-Lim implementation
        return output 
