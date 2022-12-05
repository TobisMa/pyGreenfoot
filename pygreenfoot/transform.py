from vectormath import Vector2Array
from math import pi

from pygreenfoot.math_helper import FULL_RADIAN_ANGLE


class Transform():
    
    __slots__ = ("__pos", "__rot")
    
    def __init__(self, x: int = 0, y: int = 0, rot: float = 0) -> None:
        self.__pos = Vector2Array(x, y)
        self.__rot = rot % FULL_RADIAN_ANGLE
        
    @property
    def x(self) -> int:
        """
        x-coordinate of the object using transform
        """
        return int(self.__pos.x)
    
    @x.setter
    def x(self, value: int) -> None:
        self.__pos.x = value
    
    @property
    def y(self) -> int:
        """
        y-coordinate of the object using transform
        """
        return int(self.__pos.y)
    
    @y.setter
    def y(self, value: int) -> None:
        self.__pos.y = value
        
    @property
    def rot(self) -> float:
        return self.__rot

    @rot.setter
    def rot(self, value: float) -> None:
        self.__rot = value % FULL_RADIAN_ANGLE
    
        
    
    
    