import requests
import json
from typing import Any, List, Dict, Iterator, Mapping, Union, Optional
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk

class NoahLLM(LLM):
    """CustomLLM for Noah llm_proxy."""
    noah_url = "http://localhost:6060"
    temperature: Optional[float] = 0.8
    """Adjust the randomness of the generated text (defalut: 0.8)"""
    dynatemp_range: Optional[float] = 0.0
    """Dynamic temperature range (default: 0.0, 0.0 = disabled)."""
    dynatemp_exponent: Optional[float] = 1.0
    """Dynamic temperature exponent (default: 1.0)."""
    top_k: Optional[int] = 40
    """Limit the next token selection to the K most probable tokens (default: 40)."""
    top_p: Optional[float] = 0.95
    """Limit the next token selection to a subset of tokens with a cumulative probability above a treshold P (default: 0.95)"""
    min_p: Optional[float] = 0.05
    """The minimum probability for a token to be considered, relative to the probability of the most likely token (default: 0.05)"""
    n_predict: Optional[int] = -1
    """Set the maximum number of tokens to predict when generating text.
    Note: May exceed the set limit slightly if the last token is a partial multibyte character. When 0, no tokens will be generated but the prompt is evaluated into the cache. (default: -1, -1 = infty)"""
    n_keep: Optional[int] = 0
    """Specify the number of tokens from the prompt to retain when the context size is exceeded and tokens need to be discarded. By default, this value is set to 0 (meaning no tokens are kept). Use -1 to retain all tokens from the prompt."""
    stop: Optional[List[str]] = []
    """Specify a JSON array of stopping strings. These words will not be included in the completion, so make sure to add them to the prompt for the next iteration (default: [])."""
    tfs_z: Optional[float] = 1.0
    """Enable tail free sampling with parameter z (default 1.0, 1.0 = disabled)."""
    typical_p: Optional[float] = 1.0
    """Enable locally typical sampling with parameter p (default: 1.0, 1.0 = disabled)."""
    repeat_penalty: Optional[float] = 1.1
    """Control the repetition of token sequences in the generated text (default: 1.1)."""
    repeat_last_n: Optional[int] = 64
    """Last n tokens to consider for penalizing repetition (default: 64, 0 = disabled, -1 = ctx-size)."""
    penalize_nl: Optional[bool] = True
    """Penalize newline tokens when applying the repeat penalty (default: true)."""
    presence_penalty: Optional[float] = 0.0
    """Repeat alpha presence penalty (default: 0.0, 0.0 = disabled)."""
    frequency_penalty: Optional[float] = 0.0
    """Repeat alpha frequency penalty (default: 0.0, 0.0 = disabled)"""
    penalty_prompt: Optional[str] = None
    """This will replace the prompt for the purpose of the penalty evaluation. Can be either null, a string or an array of numbers representing tokens (default: null = use the original prompt)."""
    mirostat: Optional[int] = 0
    """Enable Mirostat sampling, controlling perplexity during text generation (default: 0, 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0)."""
    mirostat_tau: Optional[float] = 5.0
    """Set the Mirostat target entropy, parameter tau (default: 5.0)."""
    mirostat_eta: Optional[float] = 0.1
    """Set the Mirostat learning rate, parameter eta (default: 0.1)."""
    # grammar_path: Optional[Union[str, Path]] = None # from pathlib import Path is needed.
    """
    grammar_path: Path to the .gbnf file that defines formal grammars
    for constraining model outputs. For instance, the grammar can be used
    to force the model to generate valid JSON or to speak exclusively in emojis. At most
    one of grammar_path and grammar should be passed in.
    """
    # grammar: Optional[Union[str, Any]] = None
    """
    grammar: formal grammar for constraining model outputs. For instance, the grammar 
    can be used to force the model to generate valid JSON or to speak exclusively in 
    emojis. At most one of grammar_path and grammar should be passed in.
    """
    seed: Optional[int] = -1
    """Set the random number generator (RNG) seed (default: -1, -1 = random seed)."""
    ignore_eos: Optional[bool] = False
    """Ignore end of stream token and continue generating (default: false)."""
    # logit_bias
    n_probs : Optional[int] = 0
    """If greater than 0, the response also contains the probabilities of top N tokens for each generated token (default: 0)"""
    min_keep: Optional[int] = 0
    """If greater than 0, force samplers to return N possible tokens at minimum (default: 0)"""
    # image_data: also exists for LMM like LLaVA.
    slot_id: Optional[int] = -1
    """Assign the completion task to an specific slot. If is -1 the task will be assigned to a Idle slot (default: -1)"""
    samplers: Optional[List[str]] = ["top_k", "tfs_z", "typical_p", "top_p", "min_p", "temperature"]
    """The order the samplers should be applied in. An array of strings representing sampler type names. If a sampler is not set, it will not be used. If a sampler is specified more than once, it will be applied multiple times. (default: ["top_k", "tfs_z", "typical_p", "top_p", "min_p", "temperature"] - these are all the available values)"""
    streaming: Optional[bool] = True
    """Stream or Not."""

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling NoahLLM."""
        # To be modified more specifically in the future.
        params = {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop": self.stop,  # key here is convention among LLM classes
            "repeat_penalty": self.repeat_penalty,
            "top_k": self.top_k,
        }
        return params

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "NoahLLM"

    def _get_parameters(self, stop: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.stop and stop is not None:
            raise ValueError("`stop` found in both the input and default params.")
        params = self._default_params
        params.pop("stop")
        params["stop"] = self.stop or stop or []
        return params

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if self.streaming:
            combined_text_output = ""
            for chunk in self._stream(
                prompt=prompt,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
            ):
                combined_text_output += chunk.text
            return combined_text_output
        else:
            params = self._get_parameters(stop)
            params = {**params, **kwargs}
            result = self.client(prompt=prompt, **params)
            return result["choices"][0]["text"]

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Example Usage:
        llm = NoahLLM()
        for chunk in llm.stream("foo bar", system_prompt="lorem", cache_prompt="ipsum"):
            print(chunk)
        """
        params = {**self._get_parameters(stop), **kwargs}
        for line in self.client_chat_completion_response(user_prompt=prompt, stream=True, **params).iter_lines():
            if line:
                chunk = GenerationChunk(
                    text=json.loads(line.decode('utf-8'))['content'],
                )
                yield chunk
                if run_manager:
                    run_manager.on_llm_new_token(token=chunk, verbose=True)

    def client_chat_completion_response(
        self,
        user_prompt:str,
        stream:bool = True,
        system_prompt:Optional[str] = None,
        cache_prompt:Optional[str] = None,
        **kwargs: Any
    ):
        if user_prompt:
            headers = {"Content-Type": "application/json"}
            data = {"prompt":user_prompt, "stream": stream, **kwargs}
            if system_prompt:
                data["system_prompt"] = system_prompt
            if cache_prompt:
                data["cache_prompt"] = cache_prompt
            return requests.post(self.noah_url+"/completion", headers=headers, data=json.dumps(data), stream=stream)
        else:
            return None

