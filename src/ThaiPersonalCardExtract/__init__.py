from .PersonalCard.PersonalCard import *
from .DrivingLicense.DrivingLicense import *
from .ThaiGovernmentLottery.ThaiGovernmentLottery import *
from .utils import Language, Provider

globals().update(PersonalCard.__dict__)
globals().update(DrivingLicense.__dict__)
globals().update(ThaiGovernmentLottery.__dict__)
globals().update(Language.__dict__)
globals().update(Provider.__dict__)
