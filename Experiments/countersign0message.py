# add to init : from .countersign0message import Countersign0Message  # noqa: F01
# modify in headers.py : identifier = 11 for COUNTER_SIGN0
# get location module : 
# import module_name
# print(module_name.__file__)
# macos : /usr/local/lib/python3.7/site-packages/cose
# pi : /home/pi/.local/lib/python3.7/site-packages/cose
# docker : /usr/local/lib/python3.7/site-packages/cose

from typing import Optional, Union, TYPE_CHECKING

import cbor2

from cose import utils
from cose.messages.cosemessage import CoseMessage
from cose.messages.signcommon import SignCommon

from cose.headers import Algorithm

if TYPE_CHECKING:
    from cose.keys.ec2 import EC2
    from cose.keys.okp import OKP
    from cose.keys.rsa import RSA

CBOR = bytes


@CoseMessage.record_cbor_tag(11)
class Countersign0Message(SignCommon):
    context = "CounterSignature0"
    cbor_tag = 11
    payload_tag = -1
    body_protected = b''
    body_unprotected = {}
    enc = b''

    @classmethod
    def from_cose_obj(cls, cose_obj, allow_unknown_attributes: bool) -> 'Countersign0Message':
        msg = super().from_cose_obj(cose_obj, allow_unknown_attributes)
        msg._signature = cose_obj.pop(0)
        return msg

    def __init__(self,
                 phdr: Optional[dict] = None,
                 uhdr: Optional[dict] = None,
                 payload: bytes = b'',
                 external_aad: bytes = b'',
                 key: Optional[Union['EC2', 'OKP']] = None,
                 *args,
                 **kwargs):
        if phdr is None:
            phdr = {}
        if uhdr is None:
            uhdr = {}

        # get protected and unprotected header of the payload + encrypted part
        self.payload_tag = cbor2.loads(payload).tag
        cose_obj = cbor2.loads(payload).value
        self.body_protected = cose_obj[0]
        self.body_unprotected = cose_obj[1]
        self.enc = cose_obj[2]

        # print(f"payload loaded : {cbor2.loads(payload)}")
        # print(f"protected : {self.body_protected}")
        # print(f"unprotected : {self.body_unprotected}")
        # print(f"enc : {self.enc}")
        # print(f"payload_tag : {self.payload_tag}")

        # packet = [self.body_protected, self.body_unprotected, self.enc]
        # print(payload == cbor2.dumps(cbor2.CBORTag(self.payload_tag, packet), default=self._custom_cbor_encoder))
        
        super().__init__(phdr, uhdr, payload, external_aad, key, *args, **kwargs)

        self._signature = b''

    @property
    def signature(self):
        return self._signature

    @property
    def _sig_structure(self):
        """
        Create the countersign_structure that needs to be signed

        :return: to_be_signed
        """
        countersign_structure = [self.context]
        countersign_structure = self._base_structure(countersign_structure)

        countersign_structure.append(self.body_protected)
        countersign_structure.append(self.phdr_encoded)
        countersign_structure.append(self.external_aad)
        countersign_structure.append(self.enc)

        return cbor2.dumps(cbor2.CBORTag(self.cbor_tag, countersign_structure))


    def encode(self, tag: bool = True, sign: bool = True, *args, **kwargs) -> CBOR:
        """ Encodes the message into a CBOR array with or without a CBOR tag. """

        if sign:
            countersign = [self.phdr_encoded, self.uhdr_encoded, self.compute_signature()]
        else:
            countersign = [self.phdr_encoded, self.uhdr_encoded]

        # add countersign to body_unprotected
        # print(f"unprotected : {self.body_unprotected}")
        self.body_unprotected[self.cbor_tag] = countersign
        # print(f"unprotected : {self.body_unprotected}")
        
        packet = [self.body_protected, self.body_unprotected, self.enc]

        if tag:
            res = cbor2.dumps(cbor2.CBORTag(self.payload_tag, packet), default=self._custom_cbor_encoder)
        else:
            res = cbor2.dumps(packet, default=self._custom_cbor_encoder)

        return res


    def verify_signature(self, *args, **kwargs) -> bool:
        unprotected_len = len(self.body_unprotected[self.cbor_tag])
        self._signature = self.body_unprotected[self.cbor_tag][unprotected_len-1]
        
        if self.phdr == {} :
            self.phdr = {Algorithm: self.key.alg}
            super().__init__(self.phdr, self.uhdr, self.payload, self.external_aad, self.key)
        
        return super().verify_signature(*args, **kwargs)


    def __repr__(self) -> str:
        phdr, uhdr = self._hdr_repr()

        return f'<COSE_CounterSign0: [{phdr}, {uhdr}, {utils.truncate(self.enc)}, ' \
               f'{utils.truncate(self._signature)}]>'

