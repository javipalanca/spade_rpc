#!/usr/bin/env python

"""Tests for `spade_rpc` package."""

import unittest

import pytest
from click.testing import CliRunner
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from spade_rpc import RPCMixin

AGENT_JID = "demo@araylop-vrain"
PWD1 = "1234"
AGENT2_JID = "demo2@araylop-vrain"
PWD2 = "4321"


@pytest.mark.asyncio
async def test_create_mixin():
    class TestAgent(RPCMixin, Agent):
        async def setup(self):
            pass

    class DummyBeh(OneShotBehaviour):
        async def run(self):
            self.kill(exit_code="Success")

    agent = TestAgent(AGENT_JID, PWD1)
    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    dummy = DummyBeh()
    agent.add_behaviour(dummy)
    await dummy.join()

    assert dummy.exit_code == "Success"

    await agent.stop()
    assert agent.is_alive() is False


@pytest.mark.asyncio
async def test_register_method():
    class TestAgent(RPCMixin, Agent):
        async def setup(self):
            def sum_service(a, b):
                return a + b

            self.rpc.register_method(sum_service, method_name="sum")

    class AskBehaviour(OneShotBehaviour):
        def __init__(self, agent_jid):
            super().__init__()
            self.agent_jid = agent_jid

        async def run(self):
            result = await self.agent.rpc.call_sync(self.agent_jid, 'sum', [3, 5])
            self.kill(exit_code=result[0])

    class ClientAgent(RPCMixin, Agent):
        def __init__(self, *args, server_jid):
            super().__init__(*args)
            self.server_jid = server_jid

        async def setup(self):
            ab = AskBehaviour(self.server_jid)
            self.add_behaviour(ab)

    agent = TestAgent(AGENT_JID, PWD1)
    await agent.start(auto_register=True)
    assert agent.is_alive() is True

    client = ClientAgent(AGENT2_JID, PWD1, server_jid=AGENT_JID)
    await client.start(auto_register=True)
    assert client.is_alive() is True

    ask = AskBehaviour(AGENT_JID)
    agent.add_behaviour(ask)
    await ask.join()

    assert ask.exit_code == 8

    await agent.stop()
    assert agent.is_alive() is False
