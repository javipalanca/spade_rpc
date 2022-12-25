import getpass
import time

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour

from spade_rpc.rpc import RPCMixin


class ServerAgent(RPCMixin, Agent):
    async def setup(self):
        def sum_service(a, b):
            return a + b

        self.rpc.register_method(sum_service, method_name="sum")


class AskBehaviour(OneShotBehaviour):
    def __init__(self, agent_jid):
        super().__init__()
        self.agent_jid = agent_jid

    async def run(self):
        result = await self.agent.rpc.call(self.agent_jid, 'sum', [3, 5])
        print(f"3 + 5 = {result[0]}")
        assert result[0] == 8

        await self.agent.stop()


class ClientAgent(RPCMixin, Agent):
    async def setup(self):
        ab = AskBehaviour(self.server_jid)
        self.add_behaviour(ab)


def main(jid, passwd):
    server_jid = f'{jid}/df'

    server_agent = ServerAgent(server_jid, passwd)
    future = server_agent.start()
    future.result()

    test_client = ClientAgent(f'client_{jid}/test', passwd)
    test_client.server_jid = server_jid

    future = test_client.start()
    future.result()

    while test_client.is_alive():
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            test_client.stop()
            break


if __name__ == "__main__":
    jid = input("JID> ")
    passwd = getpass.getpass()

    main(jid, passwd)
