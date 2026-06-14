from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.post_generate_chat_body_model import PostGenerateChatBodyModel
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.post_generate_chat_body_messages_item import PostGenerateChatBodyMessagesItem





T = TypeVar("T", bound="PostGenerateChatBody")



@_attrs_define
class PostGenerateChatBody:
    """ 
        Attributes:
            messages (list[PostGenerateChatBodyMessagesItem]): An array of messages forming the conversation history.
                Example: [{'role': 'user', 'content': 'Who are you?'}].
            system (str | Unset): Optional system instructions to guide the model's behavior. Example: You are a helpful
                assistant that provides concise answers..
            model (PostGenerateChatBodyModel | Unset): The Bedrock model to use for generating the response. Default:
                PostGenerateChatBodyModel.AMAZON_NOVA_MICRO_V10.
     """

    messages: list[PostGenerateChatBodyMessagesItem]
    system: str | Unset = UNSET
    model: PostGenerateChatBodyModel | Unset = PostGenerateChatBodyModel.AMAZON_NOVA_MICRO_V10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.post_generate_chat_body_messages_item import PostGenerateChatBodyMessagesItem
        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)



        system = self.system

        model: str | Unset = UNSET
        if not isinstance(self.model, Unset):
            model = self.model.value



        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "messages": messages,
        })
        if system is not UNSET:
            field_dict["system"] = system
        if model is not UNSET:
            field_dict["model"] = model

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_generate_chat_body_messages_item import PostGenerateChatBodyMessagesItem
        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in (_messages):
            messages_item = PostGenerateChatBodyMessagesItem.from_dict(messages_item_data)



            messages.append(messages_item)


        system = d.pop("system", UNSET)

        _model = d.pop("model", UNSET)
        model: PostGenerateChatBodyModel | Unset
        if isinstance(_model,  Unset):
            model = UNSET
        else:
            model = PostGenerateChatBodyModel(_model)




        post_generate_chat_body = cls(
            messages=messages,
            system=system,
            model=model,
        )


        post_generate_chat_body.additional_properties = d
        return post_generate_chat_body

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
