from enum import Enum

class PostGenerateChatBodyModel(str, Enum):
    AMAZON_NOVA_MICRO_V10 = "amazon.nova-micro-v1:0"
    DEEPSEEK_V3_V10 = "deepseek.v3-v1:0"
    GOOGLE_GEMMA_3_4B_IT = "google.gemma-3-4b-it"
    OPENAI_GPT_OSS_20B_10 = "openai.gpt-oss-20b-1:0"

    def __str__(self) -> str:
        return str(self.value)
