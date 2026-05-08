from blueprints.codes.eurocode.en_1992_1_1_2004 import EN_1992_1_1_2004
from blueprints.codes.formula import Formula
from blueprints.codes.latex_formula import LatexFormula
from blueprints.type_alias import MM, MM4


class FormRectangularInertia(Formula):
    """Class representing the formula for the moment of inertia of a rectangular section."""

    label = "Rectangular Inertia"
    source_document = EN_1992_1_1_2004

    def __init__(
        self,
        b: MM,
        h: MM,
    ) -> None:
        r"""[$I$] Moment of inertia (second moment of area) for a rectangular section.

        Parameters
        ----------
        b : MM
            [$b$] Base width of the rectangle [$mm$].
        h : MM
            [$h$] Height of the rectangle [$mm$].
        """
        super().__init__()
        self.b = b
        self.h = h
    
    @staticmethod
    def _evaluate(
        b: MM,
        h: MM,
    ) -> MM4:
        """Evaluates the formula, for more information see the __init__ method."""
        if b < 0:
            raise ValueError(f"Negative b: {b}. b cannot be negative")
        if h < 0:
            raise ValueError(f"Negative h: {h}. h cannot be negative")
        return (b * h ** 3) / 12

    def latex(self, n: int = 3) -> LatexFormula:
        """Returns LatexFormula object for the rectangular inertia formula."""
        return LatexFormula(
            return_symbol=r"I",
            result=f"{self:.{n}f}",
            equation=r"\frac{b \cdot h^3}{12}",
            numeric_equation=rf"\frac{{{self.b:.{n}f} \cdot {self.h:.{n}f}^3}}{{12}}",
            comparison_operator_label="=",
       )
