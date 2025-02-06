# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from asyncio import Event, Future
from typing import List, Optional

from slixmpp import ClientXMPP
from slixmpp.plugins.xep_0009 import XEP_0009
from slixmpp.plugins.xep_0009.binding import py2xml, xml2py
from slixmpp.stanza.iq import Iq

from loguru import logger


class RPCMixin(metaclass=ABCMeta):

    async def _hook_plugin_after_connection(self, *args, **kwargs):
        try:
            await super()._hook_plugin_after_connection(*args, **kwargs)
        except AttributeError:
            logger.debug("_hook_plugin_after_connection is undefined")

        self.rpc = self.RPCComponent(self._client)

    class RPCComponent:
        def __init__(self, client):
            self._client: ClientXMPP = client
            self._client.register_plugin('xep_0009')
            self._rpc_client: XEP_0009 = self._client['xep_0009']

            self._client.add_event_handler('jabber_rpc_method_call', self.handle_call)
            self._client.add_event_handler('jabber_rpc_method_response', self.handle_response)
            self._client.add_event_handler('jabber_rpc_method_fault', self.handle_fault)
            self._client.add_event_handler('jabber_rpc_error', self.handle_error)

            self.methods = {}
            self.call_event = Event()

        async def call(self, jid: str, method_name: str, params: List):
            if not isinstance(params, list):
                params = [params]

            call_stanza: Iq = self._rpc_client.make_iq_method_call(
                pto=jid,
                pmethod=method_name,
                params=py2xml(*params)
            )
            return await call_stanza.send()

        async def call_async(self, jid: str, method_name: str, params: List):
            await self.call(jid, method_name, params)

        async def call_sync(self, jid: str, method_name: str, params: List):
            res = await self.call(jid, method_name, params)
            if type(res) is Future and res.done():
                return xml2py(res['rpc_query']['method_response']['params'])

        async def handle_call(self, iq):
            try:
                name = iq['rpc_query']['method_call']['method_name']
                return self.methods[name](iq)
            except KeyError:
                params = iq['rpc_query']['method_call']['params']
                id_ = iq['id']
                to_ = iq['to']
                await self._rpc_client.make_iq_method_response_fault(id_, to_, params).send()

        @abstractmethod
        async def handle_response(self, iq):
            """
            Handles the response received from the client after a RPC request is performed.
            To override
            """
            pass

        @abstractmethod
        async def handle_fault(self, iq):
            """
            Handled a fault response received from the client if it's unable to process our request.
            To override
            """
            pass

        @abstractmethod
        async def handle_error(self, iq):
            """
            Default error
            To override
            """
            pass

        def register_method(self, handler, method_name: str):
            def method_wrapper(iq):
                params = iq['rpc_query']['method_call']['params']
                params = xml2py(params)
                _id = iq['id']

                response = handler(*params)

                if not isinstance(response, list):
                    response = [response]

                res = self._rpc_client.make_iq_method_response(
                    pid=_id,
                    pto=iq['from'],
                    params=py2xml(*response)
                )

                res.send()

            self.methods[method_name] = method_wrapper

        def unregister_method(self, method_name: str):
            try:
                self.methods.pop(method_name)
            except KeyError:
                logger.warning(f"Unable to unregister {method_name}. There's no method registered with that name")
