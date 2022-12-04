# -*- coding: utf-8 -*-
import aioxmpp.rpc.xso as rpc_xso
from spade_rpc import RPCAgent

class DFAgent(RPCAgent):
    def __init__(self, jid: str, password: str, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.jid_directory = {}
        self.method_directory = {}

    async def setup(self):    
        def register_method(stanza):
            params = self.rpc.get_params(stanza.payload.payload.params)
            method_name = params[0]
            jid = str(stanza.from_)

            if jid not in self.jid_directory:
                self.jid_directory[jid] = []
            self.jid_directory[jid].append(method_name)

            if method_name not in self.method_directory:
                self.method_directory[method_name] = []
            self.method_directory[method_name].append(jid)

            query = rpc_xso.Query(
                rpc_xso.MethodResponse(
                    rpc_xso.Params([
                        rpc_xso.Param(rpc_xso.Value(rpc_xso.boolean(True)))
                    ])
                )
            )

            return query

        def unregister_method(stanza):
            params = self.rpc.get_params(stanza.payload.payload.params)
            method_name = params[0]
            jid = str(stanza.from_)

            if jid in self.jid_directory:
                self.jid_directory[jid].remove(method_name)

            if method_name in self.method_directory:
                self.method_directory[method_name].remove(jid)
            
            query = rpc_xso.Query(
                rpc_xso.MethodResponse(
                    rpc_xso.Params([
                        rpc_xso.Param(rpc_xso.Value(rpc_xso.boolean(True)))
                    ])
                )
            )

            return query
    
        def list_methods(jid):
            if jid in self.jid_directory:
                return self.jid_directory[jid]
            else:
                return False

        def list_jids(methodname):
            if methodname in self.method_directory:
                return self.method_directory[methodname]
            else:
                return False

        self.rpc.rpc_server.register_method(register_method, 'register_method')
        self.rpc.rpc_server.register_method(unregister_method, 'unregister_method')
        self.rpc.register_method(list_methods, 'list_methods')
        self.rpc.register_method(list_jids, 'list_jids')