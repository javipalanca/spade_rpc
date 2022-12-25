# -*- coding: utf-8 -*-
import datetime as dt
from abc import ABCMeta
from typing import List, Callable

import aioxmpp
import aioxmpp.rpc.xso as rpc_xso
from loguru import logger

Param = Union[int, float, str, bool, dt.datetime, list, dict]

class RPCMixin(metaclass=ABCMeta):

    async def _hook_plugin_after_connection(self, *args, **kwargs):
        try:
            await super()._hook_plugin_after_connection(*args, **kwargs)
        except AttributeError:
            logger.debug("_hook_plugin_after_connection is undefined")

        self.rpc = self.RPCComponent(self.client)

    class RPCComponent:
        type_class = {
            int: rpc_xso.i4,
            int: rpc_xso.integer,
            str: rpc_xso.string,
            float: rpc_xso.double,
            str: rpc_xso.base64,
            bool: rpc_xso.boolean,
            dt.datetime: rpc_xso.datetime,
            list: rpc_xso.array,
            dict: rpc_xso.struct
        }

        class_type = {v: k for k, v in type_class.items()}

        def __init__(self, client):
            self.client = client
            self.rpc_client = self.client.summon(aioxmpp.RPCClient)
            self.rpc_server = self.client.summon(aioxmpp.RPCServer)

        def parse_param(self, param: Param) -> rpc_xso.Value:
            if type(param) == list:
                value = rpc_xso.array(rpc_xso.data([self.parse_param(x) for x in param]))
            elif type(param) == dict:
                members = [rpc_xso.member(rpc_xso.name(key), self.parse_param(value)) for key, value in param.items()]
                value = rpc_xso.struct(members)
            else:
                value = self.type_class[type(param)](param)

            return rpc_xso.Value(value)

        def parse_params(self, params: List[Param]) -> rpc_xso.Params:
            return rpc_xso.Params([rpc_xso.Param(self.parse_param(x)) for x in params])

        def get_param(self, xso_param):
            if type(xso_param) == rpc_xso.array:
                return [self.get_param(x.value) for x in xso_param.data.data]
            elif type(xso_param) == rpc_xso.struct:
                return {member.name.name: self.get_param(member.value.value) for member in xso_param.members}
            else:
                return self.class_type[type(xso_param)](xso_param.value)

        def get_params(self, xso_params):
            return [self.get_param(param.value.value) for param in xso_params.params]

        async def call(self, jid: str, method_name: str, params: List[Param]) -> List[Param]:
            if not isinstance(params, list):
                params = [params]

            query = rpc_xso.Query(
                rpc_xso.MethodCall(
                    rpc_xso.MethodName(method_name),
                    self.parse_params(params)
                )
            )

            response = await self.rpc_client.call_method(aioxmpp.JID.fromstr(jid), query)
            return self.get_params(response.payload.params)

        def register_method(self, handler: Callable[..., List[Param]],
                            method_name: str,
                            is_allowed: Optional[Callable[[aioxmpp.JID], bool]] = None):
            def method_wrapper(stanza):
                params = self.get_params(stanza.payload.payload.params)

                response = handler(*params)

                if not isinstance(response, list):
                    response = [response]

                query = rpc_xso.Query(
                    rpc_xso.MethodResponse(
                        self.parse_params(response)
                    )
                )

                return query

            return self.rpc_server.register_method(method_wrapper, method_name, is_allowed)

        def unregister_method(self, method_name: str):
            return self.rpc_server.unregister_method(self, method_name)
