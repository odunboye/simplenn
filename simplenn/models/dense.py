import numpy as np
from ..model import ModelWithParameters

from ..initializers import  Initializer,Zero,RandomNormal

from .linear import Linear
from . import activations
from .bias import Bias

activation_dict = {"id": activations.Identity,
                   "relu": activations.ReLU,
                   "tanh": activations.TanH,
                   "sigmoid": activations.Sigmoid,
                   "softmax": activations.Softmax,
                   }

class Dense(ModelWithParameters):
    '''
    A Dense layer simplifies the definition of networks by producing a common block
    that applies a linear, bias and activation function, in that order, to an input, ie
    y = activation(wx+b), where w and b are the parameters of the Linear and Bias models,
    and activation is the function of an activation Layer.

    Therefore, a defining a Dense layer such as:

    ```
    [...
    Dense(input_size,output_size,activation_name="relu")
    ]
    ```

    Is equivalent to:

    ```[...
    Linear(input_size,output_size),
    Bias(output_size)
    ReLu(),...]
    ```

    By default, no activation is used (actually, the Identity activation is used, which
    is equivalent). Implemented activations:
    * id
    * relu
    * tanh
    * sigmoid
    * softmax
    '''
    def __init__(self, input_size:int, output_size:int,activation_name:str=None,
                 linear_initializer:Initializer=RandomNormal(), bias_initializer:Initializer=Zero(), name=None):
        self.linear = Linear(input_size,output_size,initializer=linear_initializer)
        self.bias = Bias(output_size,initializer=bias_initializer)

        if activation_name is None:
            activation_name = "id"
        if activation_name in activation_dict:
            self.activation = activation_dict[activation_name]()
        else:
            raise ValueError(f"Unknown activation function {activation_name}. Available activations: {','.join(activation_dict.keys())}")

        super().__init__(name=name)
        # add activation name to Dense name
        self.name+=f"({activation_name})"

    def forward_with_cache(self, x:np.ndarray):
        # calculate and return activation(bias(linear(x)))

        ### COMPLETAR INICIO ###
        y_linear,cache_linear = self.linear.forward_with_cache(x)
        y_bias,cache_bias =self.bias.forward_with_cache(y_linear)
        y_activation,cache_activation= self.activation.forward_with_cache(y_bias)
        ### COMPLETAR FIN ###
        return y_activation, (cache_linear,cache_bias,cache_activation)

    def backward(self,δEδy:np.ndarray,cache):
        # Compute gradients for the parameters of the bias, linear and activation function
        # It is possible that the activation function does not have any parameters
        # (ie, δEδactivation = {})
        (cache_linear,cache_bias,cache_activation) = cache
        δEδbias,δEδlinear,δEδactivation={},{},{}

        ### COMPLETAR INICIO ###
        δEδx_activation,δEδactivation = self.activation.backward(δEδy,cache_activation)
        δEδx_bias,δEδbias =self.bias.backward(δEδx_activation,cache_bias)
        δEδx,δEδlinear =self.linear.backward(δEδx_bias,cache_linear)
        ### COMPLETAR FIN ###

        # combine gradients for parameters from dense, linear and activation models
        δEδdense ={**δEδbias, **δEδlinear,**δEδactivation}
        return δEδx,δEδdense


    def get_parameters(self):
        # returns the combination of parameters of all models
        # assumes no Layer uses the same parameter names
        # ie: Linear has `w`, bias has `b` and activation
        # has a different parameter name (if it has any).
        p_linear = self.linear.get_parameters()
        p_bias = self.bias.get_parameters()
        p_activation = self.activation.get_parameters()
        p = {**p_linear, **p_bias,**p_activation}
        return p

