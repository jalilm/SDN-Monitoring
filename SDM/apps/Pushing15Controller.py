from ryu.ofproto import ofproto_v1_5

from SDM.apps.PushingController import PushingController


class Pushing15Controller(PushingController):
    OFP_VERSIONS = [ofproto_v1_5.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Pushing15Controller, self).__init__(*args, **kwargs)
