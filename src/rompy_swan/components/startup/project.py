"""SWAN PROJECT component."""

from typing import Literal, Optional

from pydantic import Field

from rompy_swan.components.base import BaseComponent


class PROJECT(BaseComponent):
    """SWAN Project.

    .. code-block:: text

        PROJECT 'name' 'nr' 'title' 'title2 'title3'

    With this required command the user defines a number of strings to identify the
    SWAN run (project name e.g., an engineering project) in the print and plot file.

    Examples
    --------

    .. ipython:: python
        :okwarning:

        from rompy_swan.components.startup.project import PROJECT
        proj = PROJECT(nr="01")
        print(proj.render())
        proj = PROJECT(
            name="waus",
            nr="001",
            title1="Western Australia",
            title2="Perth Nest"
        )
        print(proj.render())

    """

    model_type: Literal["project", "PROJECT"] = Field(
        default="project",
        description="Model type discriminator",
    )
    name: Optional[str] = Field(
        default=None,
        description="Is the name of the project, at most 16 characters long",
        max_length=16,
    )
    nr: str = Field(
        description=(
            "Is the run identification (to be provided as a character string; e.g. "
            "the run number) to distinguish this run among other runs for the same "
            "project; it is at most 4 characters long. It is the only required "
            "information in this command."
        ),
        max_length=4,
    )
    title1: Optional[str] = Field(
        default=None,
        description=(
            "A string of at most 72 characters provided by the user to appear in the "
            "output of the program for the user's convenience (SWAN default: blanks)"
        ),
        max_length=72,
    )
    title2: Optional[str] = Field(
        default=None, description="Same as 'title1'", max_length=72
    )
    title3: Optional[str] = Field(
        default=None, description="Same as 'title1'", max_length=72
    )

    def cmd(self) -> str:
        repr = "PROJECT"
        if self.name is not None:
            repr += f" name='{self.name}'"
        repr += f" nr='{self.nr}'"
        if self.title1 is not None:
            repr += f" title1='{self.title1}'"
        if self.title2 is not None:
            repr += f" title2='{self.title2}'"
        if self.title3 is not None:
            repr += f" title3='{self.title3}'"
        return repr
