from blueprints.codes.eurocode.en_1992_1_1_2004 import EN_1992_1_1_2004
from blueprints.codes.formula import Formula
from blueprints.codes.latex_formula import LatexFormula
from blueprints.type_alias import MPA, DIMENSIONLESS


class FormShearModulus(Formula):
    """Class representing the formula for the shear modulus."""

    label = "Shear Modulus"
    source_document = EN_1992_1_1_2004

    def __init__(
        self,
        e: MPA,
        poisson_ratio: DIMENSIONLESS,
    ) -> None:
        r"""[$G$] Shear Modulus.

        Parameters
        ----------
        e : MPA
            [$E$] Young's Modulus [$MPa$].
        poisson_ratio : DIMENSIONLESS
            [$\nu$] Poisson's ratio [-].
        """
        super().__init__()
        self.e = e
        self.poisson_ratio = poisson_ratio

    @staticmethod
    def _evaluate(
        e: MPA,
        poisson_ratio: DIMENSIONLESS,
    ) -> MPA:
        """Evaluates the formula, for more information see the __init__ method."""
        if e < 0:
            raise ValueError(f"Negative e: {e}. e cannot be negative")
        if poisson_ratio < -1:
             # Poisson ratio can be negative in theory (auxetic materials), but usually > -1. 
             # Standard engineering materials are 0 to 0.5. 
             # Let's just warn or allow it, but strictly denominator shouldn't be zero.
             # 1 + nu = 0 -> nu = -1.
             pass
        
        if (1 + poisson_ratio) == 0:
             raise ValueError(f"Invalid poisson_ratio: {poisson_ratio}. Denominator cannot be zero.")

        return e / (2 * (1 + poisson_ratio))

    def latex(self, n: int = 3) -> LatexFormula:
        """Returns LatexFormula object for the shear modulus formula."""
        return LatexFormula(
            return_symbol=r"G",
            result=f"{self:.{n}f}",
            equation=r"\frac{E}{2(1 + \nu)}",
            numeric_equation=rf"\frac{{{self.e:.{n}f}}}{{2(1 + {self.poisson_ratio:.{n}f})}}",
            comparison_operator_label="=",
        )


if __name__ == "__main__":
    try:
        e_val = 210000.0
        nu_val = 0.3
        shear_mod = FormShearModulus(e=e_val, poisson_ratio=nu_val)
        print(f"Calculated Shear Modulus for E={e_val}, nu={nu_val}: {float(shear_mod)}")
        print(f"Latex: {shear_mod.latex().equation}")
    except Exception as e:
        print(f"Error running FormShearModulus: {e}")

