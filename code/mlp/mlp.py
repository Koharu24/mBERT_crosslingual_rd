r"""undocumented"""

__all__ = ["MLP"]

import torch
import torch.nn as nn

from .initial_parameter import initial_parameter


class MLP(nn.Module):
    """
    Examples::

        >>> net1 = MLP([5, 10, 5])
        >>> net2 = MLP([5, 10, 5], 'tanh')
        >>> net3 = MLP([5, 6, 7, 8, 5], 'tanh')
        >>> net4 = MLP([5, 6, 7, 8, 5], 'relu', output_activation='tanh')
        >>> net5 = MLP([5, 6, 7, 8, 5], ['tanh', 'relu', 'tanh'], 'tanh')
        >>> for net in [net1, net2, net3, net4, net5]:
        >>>     x = torch.randn(5, 5)
        >>>     y = net(x)
        >>>     print(x)
        >>>     print(y)
    """

    def __init__(
        self,
        size_layer,
        activation="relu",
        output_activation=None,
        initial_method=None,
        dropout=0.0,
    ):
        r"""

        :param List[int] size_layer: 一个int的列表，用来定义MLP的层数，列表中的数字为每一层是hidden数目。MLP的层数为 len(size_layer) - 1
        :param Union[str,func,List[str]] activation: 一个字符串或者函数的列表，用来定义每一个隐层的激活函数，字符串包括relu，tanh和
            sigmoid，默认值为relu
        :param Union[str,func] output_activation:  字符串或者函数，用来定义输出层的激活函数，默认值为None，表示输出层没有激活函数
        :param str initial_method: 参数初始化方式
        :param float dropout: dropout概率，默认值为0
        """
        super(MLP, self).__init__()
        self.hiddens = nn.ModuleList()
        self.output_activation = output_activation
        for i in range(1, len(size_layer)):
            if i + 1 == len(size_layer):
                self.output = nn.Linear(size_layer[i - 1], size_layer[i])
            else:
                self.hiddens.append(nn.Linear(size_layer[i - 1], size_layer[i]))

        self.dropout = nn.Dropout(p=dropout)

        actives = {
            "relu": nn.ReLU(),
            "tanh": nn.Tanh(),
            "sigmoid": nn.Sigmoid(),
        }
        if not isinstance(activation, list):
            activation = [activation] * (len(size_layer) - 2)
        elif len(activation) == len(size_layer) - 2:
            pass
        else:
            raise ValueError(
                f"the length of activation function list except {len(size_layer) - 2} but got {len(activation)}!"
            )
        self.hidden_active = []
        for func in activation:
            if callable(func):
                self.hidden_active.append(func)
            elif func.lower() in actives:
                self.hidden_active.append(actives[func])
            else:
                raise ValueError(
                    "should set activation correctly: {}".format(activation)
                )
        if self.output_activation is not None:
            if callable(self.output_activation):
                pass
            elif self.output_activation.lower() in actives:
                self.output_activation = actives[self.output_activation]
            else:
                raise ValueError(
                    "should set activation correctly: {}".format(activation)
                )
        initial_parameter(self, initial_method)

    def forward(self, x):
        r"""
        :param torch.Tensor x: MLP接受的输入
        :return: torch.Tensor : MLP的输出结果
        """
        for layer, func in zip(self.hiddens, self.hidden_active):
            x = self.dropout(func(layer(x)))
        x = self.output(x)
        if self.output_activation is not None:
            x = self.output_activation(x)
        x = self.dropout(x)
        return x
