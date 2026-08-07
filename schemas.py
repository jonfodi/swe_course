"""Wire shapes for the API.

These are deliberately separate from the internal structures in cyber.py.
cyber.py owns how data is *stored* (tuples, sets, whatever is fast for the
query); this module owns what goes *over the wire*. Keeping them apart means
an internal refactor isn't automatically a breaking API change.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthLogOut(BaseModel):
    # from_attributes lets pydantic read the NamedTuple's fields by name
    model_config = ConfigDict(from_attributes=True)

    timestamp: datetime
    src_ip: str
    username: str
    success: bool


class WhoAmIOut(BaseModel):
    """Echo of the resolved identity -- who the server thinks is asking."""

    model_config = ConfigDict(from_attributes=True)

    user_id: str
    org_id: str
