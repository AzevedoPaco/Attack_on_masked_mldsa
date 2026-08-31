from tqdm.notebook import trange
import matplotlib.pyplot as plt
import numpy as np
import math 

from binascii import hexlify, unhexlify
import estraces

from collections import Counter
import scared

import struct 
import copy

import random
import os 
import sys

format_types = [{1 : "B", 2 : "H", 4 : "I" , 8: "Q"},
                {1 : "b", 2 : "h", 4 : "i" , 8: "q"}]


def hexstr_to_int(hexstr: str, signed: bool = True) -> int:
    """
    Convert a hexadecimal string to an integer.

    This function takes a hexadecimal string representing bytes and maps it 
    to an integer. Depending on the flag `signed` each byte can be interpreted as signed 
    or unsigned.
    
    Inputs:
    -------
    hexstr     (str)            : A string containing hexadecimal digits representing a byte.
    signed     (bool | optional): Flag to interpret the bytes as signed integers (default is True).

    Outputs:
    -------
    int_ (int): The converted integer representation of the input hexadecimal string. 
    """
    bytes_ = bytes.fromhex(hexstr)
    format_ = format_types[signed][len(hexstr)//2]
    int_ = struct.unpack(f"<{format_}", bytes_)[0]
    return int_


def int_to_hexstr(int_: int, nb_bytes: int = 4, signed: bool = True) -> str:
    """
    Convert an integer to a hexadecimal string.

    This function converts an integer into its hexadecimal string representation on nb_bytes bytes. 
    Depending on the flag `signed`, the integer can be interpreted as signed or unsigned. 
    The resulting hexadecimal string represents the bytes in big-endian order.

    Inputs:
    -------
    num      (int)            : The integer to convert to a hexadecimal string.
    nb_bytes (int  | optional): The number of bytes to represent the integer (default is 4).
                                   The output will be padded with leading zeros if necessary.
    signed   (bool | optional): Flag to interpret the integer as a signed value (default is True).

    Outputs:
    -------
    (str): The hexadecimal string representation of the input integer, 
           formatted as two hexadecimal digits per byte.
    """
    bytes_ = int_.to_bytes(nb_bytes, "big", signed = signed)
    return "".join(format(byte, "02x") for byte in reversed(bytes_))


def intlist_to_int (intlist: list[int], signed: bool = True) -> int:
    """
    Convert a list of integers into an integer.

    This function takes a list of integers, where each integer represents a byte, 
    and converts the entire list into a single integer. 
    Depending on the flag `signed`, the integers can be interpreted as signed or unsigned. 
    The  bytes are processed in reverse order.

    Inputs:
    -------
    intlist (list[int])      : List of integers.
    signed  (bool | optional): Flag to interpret the resulting integer as signed (default is True).

    Outputs:
    -------
    (int) : The converted integer representation of the input list.
    """
    bytes_ = bytes(reversed(intlist))
    return int.from_bytes(bytes_, "big", signed = signed)


def int_to_intlist(int_:int, nb_bytes:int = 4, signed: bool = True) -> list[int]:
    """
    Convert an integer to a list of integers.

    This function converts an integer into a list of integers, where each integer 
    in the list corresponds to a byte (8 bits) of the original integer. The output 
    list is generated in reverse order, reflecting big-endian byte order.

    Inputs:
    -------
    num      (int)            : The integer to convert into a list of byte integers.
    nb_bytes (int  | optional): The number of bytes to represent the integer (default is 4).
                                The output list will contain leading zeros if necessary.
    signed   (bool | optional): Flag to interpret the integer as a signed value (default is True).

    Outputs:
    -------
    (list[int]): A list of integers representing the bytes of the input integer.
    """
    return [byy for byy in reversed((int_).to_bytes(nb_bytes, "big", signed = signed))]


def hexstr_to_intlist(hex_string: str, signed: bool = True) -> list[int]:
    """
    Convert a hexadecimal string to a list of integers.

    Each pair of hexadecimal characters in the string is interpreted as a byte.
    If the `signed` parameter is True, bytes with a value of 128 or greater
    are converted to their signed integer equivalent in the range of [-128, 127].
    
    Inputs:
    -------
    hex_string (str)            : Hexadecimal string, with an even number of characters.
    signed     (bool | optional): Flag to interpret the bytes as signed integers (default is True).

    Outputs:
    -------
    (list[int]): List of integers converted from the hexadecimal string. 
                 The integers will be in the range of [-128, 127] if `signed` = True,
                 and in the range of [0, 255] if `signed` = False.
    """
    int_gen = (int(hex_string[i:i + 2], 16) for i in range(0, len(hex_string), 2))
    return [int_ - 256 * (int_ >> 7 and signed) for int_ in int_gen]


def intlist_to_hextsr(intlist: list[int]) -> str:
    """
    Convert a list of integers to a hexadecimal string.

    Each integer in the list is treated as a byte. 
    The function converts each integer to its hexadecimal representation and concatenating them.
    
    Inputs:
    -------
    intlist (list[int]): Int list to convert to a hexadecimal string. The integers should be in the 
                         range of [-128, 255], as negative values are wrapped to fit within an unsigned byte.

    Outputs:
    -------
    (str): A hexadecimal string representation of the input list, where each 
           integer is represented as two hexadecimal digits. For example, an 
           integer value of 255 will be represented as 'ff'.
    """
    return ''.join(f'{x  & 0xff:02x}' for x in intlist)


def HW(int_:int) -> int:
    """
    Calculate the Hamming Weight of an integer.

    Inputs:
    -------
    int_ (int) : The input integer for which to calculate the Hamming Weight. 

    Outputs:
    -------
    (int): The Hamming Weight of int_, which is the count of '1' bits in its binary representation.
    """
    return bin(int_).count('1')


def intlist_to_cw(intlist):
    """
    Convert a list of integers to a bytes representation in C-style.

    Inputs:
    -------
    intlist (list[int]): List of integers to be converted, where each integer should be in  [0, 255].

    Outputs:
    --------
    (bytes): A bytes object representing the input integer list in C-style format, 
             with each integer converted to a single byte.
    """
    nparray_uint8 = np.array(intlist, dtype=np.uint8)
    return np.ndarray.tobytes(nparray_uint8, 'C')


def disconnect_cw():
    """
    Disconnects the Chipwhisperer
    
    Inputs:
    -------

    Outputs:
    --------
    """
    scope.dis()
    target.dis()
    print("ChipWhisperer disconnected, Goodbye! 😢")