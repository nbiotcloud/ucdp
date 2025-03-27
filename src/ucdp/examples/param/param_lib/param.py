#
# MIT License
#
# Copyright (c) 2024-2025 nbiotcloud
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

"""Param."""

import ucdp as u


class ParamMod(u.AMod):
    """Example Module With Parameters."""

    def _build(self):
        parser = self.parser
        # a module parameter which can be set at instantiation
        param_p = self.add_param(u.IntegerType(default=10), "param_p")
        # a parameter which is derived by a formula from a previous parameter
        width_p = self.add_param(u.IntegerType(default=parser.log2(param_p + 1)), "width_p")
        # just another parameter
        default_p = self.add_param(u.IntegerType(default=param_p), "default_p")

        # ports which depend on the parameter above
        self.add_port(u.UintType(param_p), "data_i")
        self.add_port(u.UintType(width_p), "cnt_o")

        # an internal constant
        self.add_const(u.UintType(param_p, default=default_p), "const_c")
