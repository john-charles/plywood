"""
This file is part of plywood.
    
    Copyright 2013 John-Charles D. Sokolow - <john.charles.sokolow@gmail.com>

    plywood is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    plywood is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with plywood.  If not, see <http://www.gnu.org/licenses/>.
    
Please see README for usage details.   

Kinds. I Got the idea for this from the following article.
    http://www.joelonsoftware.com/articles/Wrong.html
    
Although kinds are technically types, their subtly different.
Basically a kind is a standard type, string, int, etc. Which has
a limited set of allowable contents.

This solves my problem if how this framework will manipulate
safe and potentially unsafe user submitted data.

Names
    ss = SimpleString
    cs = ComplexString
    ds = DangerousString

"""
__all__ = ['cs_from_ds','ss_from_ds', 'hs_from_ds']

import random

SS_ERROR = "%s strings cannot contain the %s character!"
PERMISSABLE = range(48, 58) + range(65, 91) + range(97, 122)
SS_PERMISSABLE = PERMISSABLE + [32, 95]
CS_PERMISSABLE = SS_PERMISSABLE + [45, 47, 91, 92, 93, 95, 124]
#EM_PERMISSABLE = PERMISSABLE + [64, 46]

ES_TBL = [
    ('quot', '"'), ('amp', '&'), ('apos', "'"), ('lt', '<'), ('gt', '>'),
    ('nbsp', ''), ('iexcl', '\xc2\xa1'), ('cent', '\xc2\xa2'), ('pound', '\xc2\xa3'),
    ('curren', '\xc2\xa4'), ('yen', '\xc2\xa5'), ('brvbar', '\xc2\xa6'), ('sect', '\xc2\xa7'),
    ('uml', '\xc2\xa8'), ('copy', '\xc2\xa9'), ('ordf', '\xc2\xaa'), ('laquo', '\xc2\xab'),
    ('not', '\xc2\xac'), ('reg', '\xc2\xae'), ('macr', '\xc2\xaf'),
    ('deg', '\xc2\xb0'), ('plusmn', '\xc2\xb1'), ('sup2', '\xc2\xb2'), ('sup3', '\xc2\xb3'),
    ('acute', '\xc2\xb4'), ('micro', '\xc2\xb5'), ('para', '\xc2\xb6'), ('middot', '\xc2\xb7'),
    ('cedil', '\xc2\xb8'), ('sup1', '\xc2\xb9'), ('ordm', '\xc2\xba'), ('raquo', '\xc2\xbb'),
    ('frac14', '\xc2\xbc'), ('frac12', '\xc2\xbd'), ('frac34', '\xc2\xbe'), ('iquest', '\xc2\xbf'),
    ('Agrave', '\xc3\x80'), ('Aacute', '\xc3\x81'), ('Acirc', '\xc3\x82'), ('Atilde', '\xc3\x83'),
    ('Auml', '\xc3\x84'), ('Aring', '\xc3\x85'), ('AElig', '\xc3\x86'), ('Ccedil', '\xc3\x87'),
    ('Egrave', '\xc3\x88'), ('Eacute', '\xc3\x89'), ('Ecirc', '\xc3\x8a'), ('Euml', '\xc3\x8b'),
    ('Igrave', '\xc3\x8c'), ('Iacute', '\xc3\x8d'), ('Icirc', '\xc3\x8e'), ('Iuml', '\xc3\x8f'),
    ('ETH', '\xc3\x90'), ('Ntilde', '\xc3\x91'), ('Ograve', '\xc3\x92'), ('Oacute', '\xc3\x93'),
    ('Ocirc', '\xc3\x94'), ('Otilde', '\xc3\x95'), ('Ouml', '\xc3\x96'), ('times', '\xc3\x97'),
    ('Oslash', '\xc3\x98'), ('Ugrave', '\xc3\x99'), ('Uacute', '\xc3\x9a'), ('Ucirc', '\xc3\x9b'),
    ('Uuml', '\xc3\x9c'), ('Yacute', '\xc3\x9d'), ('THORN', '\xc3\x9e'), ('szlig', '\xc3\x9f'),
    ('agrave', '\xc3\xa0'), ('aacute', '\xc3\xa1'), ('acirc', '\xc3\xa2'), ('atilde', '\xc3\xa3'),
    ('auml', '\xc3\xa4'), ('aring', '\xc3\xa5'), ('aelig', '\xc3\xa6'), ('ccedil', '\xc3\xa7'),
    ('egrave', '\xc3\xa8'), ('eacute', '\xc3\xa9'), ('ecirc', '\xc3\xaa'), ('euml', '\xc3\xab'),
    ('igrave', '\xc3\xac'), ('iacute', '\xc3\xad'), ('icirc', '\xc3\xae'), ('iuml', '\xc3\xaf'),
    ('eth', '\xc3\xb0'), ('ntilde', '\xc3\xb1'), ('ograve', '\xc3\xb2'), ('oacute', '\xc3\xb3'),
    ('ocirc', '\xc3\xb4'), ('otilde', '\xc3\xb5'), ('ouml', '\xc3\xb6'), ('divide', '\xc3\xb7'),
    ('oslash', '\xc3\xb8'), ('ugrave', '\xc3\xb9'), ('uacute', '\xc3\xba'), ('ucirc', '\xc3\xbb'),
    ('uuml', '\xc3\xbc'), ('yacute', '\xc3\xbd'), ('thorn', '\xc3\xbe'), ('yuml', '\xc3\xbf'),
    ('OElig', '\xc5\x92'), ('oelig', '\xc5\x93'), ('Scaron', '\xc5\xa0'), ('scaron', '\xc5\xa1'),
    ('Yuml', '\xc5\xb8'), ('fnof', '\xc6\x92'), ('circ', '\xcb\x86'), ('tilde', '\xcb\x9c'),
    ('Alpha', '\xce\x91'), ('Beta', '\xce\x92'), ('Gamma', '\xce\x93'), ('Delta', '\xce\x94'),
    ('Epsilon', '\xce\x95'), ('Zeta', '\xce\x96'), ('Eta', '\xce\x97'), ('Theta', '\xce\x98'),
    ('Iota', '\xce\x99'), ('Kappa', '\xce\x9a'), ('Lambda', '\xce\x9b'), ('Mu', '\xce\x9c'),
    ('Nu', '\xce\x9d'), ('Xi', '\xce\x9e'), ('Omicron', '\xce\x9f'), ('Pi', '\xce\xa0'),
    ('Rho', '\xce\xa1'), ('Sigma', '\xce\xa3'), ('Tau', '\xce\xa4'), ('Upsilon', '\xce\xa5'),
    ('Phi', '\xce\xa6'), ('Chi', '\xce\xa7'), ('Psi', '\xce\xa8'), ('Omega', '\xce\xa9'),
    ('alpha', '\xce\xb1'), ('beta', '\xce\xb2'), ('gamma', '\xce\xb3'), ('delta', '\xce\xb4'),
    ('epsilon', '\xce\xb5'), ('zeta', '\xce\xb6'), ('eta', '\xce\xb7'), ('theta', '\xce\xb8'),
    ('iota', '\xce\xb9'), ('kappa', '\xce\xba'), ('lambda', '\xce\xbb'), ('mu', '\xce\xbc'),
    ('nu', '\xce\xbd'), ('xi', '\xce\xbe'), ('omicron', '\xce\xbf'), ('pi', '\xcf\x80'),
    ('rho', '\xcf\x81'), ('sigmaf', '\xcf\x82'), ('sigma', '\xcf\x83'), ('tau', '\xcf\x84'),
    ('upsilon', '\xcf\x85'), ('phi', '\xcf\x86'), ('chi', '\xcf\x87'), ('psi', '\xcf\x88'),
    ('omega', '\xcf\x89'), ('thetasym', '\xcf\x91'), ('upsih', '\xcf\x92'), ('piv', '\xcf\x96'),
    ('ensp', '\xe2\x80\x82'), ('emsp', '\xe2\x80\x83'), ('thinsp', '\xe2\x80\x89'), ('ndash', '\xe2\x80\x93'),
    ('mdash', '\xe2\x80\x94'), ('lsquo', '\xe2\x80\x98'), ('rsquo', '\xe2\x80\x99'), ('sbquo', '\xe2\x80\x9a'),
    ('ldquo', '\xe2\x80\x9c'), ('rdquo', '\xe2\x80\x9d'), ('bdquo', '\xe2\x80\x9e'), ('dagger', '\xe2\x80\xa0'),
    ('Dagger', '\xe2\x80\xa1'), ('bull', '\xe2\x80\xa2'), ('hellip', '\xe2\x80\xa6'), ('permil', '\xe2\x80\xb0'),
    ('prime', '\xe2\x80\xb2'), ('Prime', '\xe2\x80\xb3'), ('lsaquo', '\xe2\x80\xb9'), ('rsaquo', '\xe2\x80\xba'),
    ('oline', '\xe2\x80\xbe'), ('frasl', '\xe2\x81\x84'), ('euro', '\xe2\x82\xac'), ('image', '\xe2\x84\x91'),
    ('weierp', '\xe2\x84\x98'), ('real', '\xe2\x84\x9c'), ('trade', '\xe2\x84\xa2'), ('alefsym', '\xe2\x84\xb5'),
    ('larr', '\xe2\x86\x90'), ('uarr', '\xe2\x86\x91'), ('rarr', '\xe2\x86\x92'), ('darr', '\xe2\x86\x93'),
    ('harr', '\xe2\x86\x94'), ('crarr', '\xe2\x86\xb5'), ('lArr', '\xe2\x87\x90'), ('uArr', '\xe2\x87\x91'),
    ('rArr', '\xe2\x87\x92'), ('dArr', '\xe2\x87\x93'), ('hArr', '\xe2\x87\x94'), ('forall', '\xe2\x88\x80'),
    ('part', '\xe2\x88\x82'), ('exist', '\xe2\x88\x83'), ('empty', '\xe2\x88\x85'), ('nabla', '\xe2\x88\x87'),
    ('isin', '\xe2\x88\x88'), ('notin', '\xe2\x88\x89'), ('ni', '\xe2\x88\x8b'), ('prod', '\xe2\x88\x8f'),
    ('sum', '\xe2\x88\x91'), ('minus', '\xe2\x88\x92'), ('lowast', '\xe2\x88\x97'), ('radic', '\xe2\x88\x9a'),
    ('prop', '\xe2\x88\x9d'), ('infin', '\xe2\x88\x9e'), ('ang', '\xe2\x88\xa0'), ('and', '\xe2\x88\xa7'),
    ('or', '\xe2\x88\xa8'), ('cap', '\xe2\x88\xa9'), ('cup', '\xe2\x88\xaa'), ('int', '\xe2\x88\xab'),
    ('there4', '\xe2\x88\xb4'), ('sim', '\xe2\x88\xbc'), ('cong', '\xe2\x89\x85'), ('asymp', '\xe2\x89\x88'),
    ('ne', '\xe2\x89\xa0'), ('equiv', '\xe2\x89\xa1'), ('le', '\xe2\x89\xa4'), ('ge', '\xe2\x89\xa5'),
    ('sub', '\xe2\x8a\x82'), ('sup', '\xe2\x8a\x83'), ('nsub', '\xe2\x8a\x84'), ('sube', '\xe2\x8a\x86'),
    ('supe', '\xe2\x8a\x87'), ('oplus', '\xe2\x8a\x95'), ('otimes', '\xe2\x8a\x97'), ('perp', '\xe2\x8a\xa5'),
    ('sdot', '\xe2\x8b\x85'), ('lceil', '\xe2\x8c\x88'), ('rceil', '\xe2\x8c\x89'), ('lfloor', '\xe2\x8c\x8a'),
    ('rfloor', '\xe2\x8c\x8b'), ('lang', '\xe2\x8c\xa9'), ('rang', '\xe2\x8c\xaa'), ('loz', '\xe2\x97\x8a'),
    ('spades', '\xe2\x99\xa0'), ('clubs', '\xe2\x99\xa3'), ('hearts', '\xe2\x99\xa5'), ('diams', '\xe2\x99\xa6')
]

SE_TBL = [
    ('"', 'quot'), ('&', 'amp'), ("'", 'apos'), ('<', 'lt'),
    ('>', 'gt'), ('\xc2\xa1', 'iexcl'), ('\xc2\xa2', 'cent'), ('\xc2\xa3', 'pound'),
    ('\xc2\xa4', 'curren'), ('\xc2\xa5', 'yen'), ('\xc2\xa6', 'brvbar'), ('\xc2\xa7', 'sect'),
    ('\xc2\xa8', 'uml'), ('\xc2\xa9', 'copy'), ('\xc2\xaa', 'ordf'), ('\xc2\xab', 'laquo'),
    ('\xc2\xac', 'not'), ('\xc2\xae', 'reg'), ('\xc2\xaf', 'macr'), ('\xc2\xb0', 'deg'),
    ('\xc2\xb1', 'plusmn'), ('\xc2\xb2', 'sup2'), ('\xc2\xb3', 'sup3'), ('\xc2\xb4', 'acute'),
    ('\xc2\xb5', 'micro'), ('\xc2\xb6', 'para'), ('\xc2\xb7', 'middot'), ('\xc2\xb8', 'cedil'),
    ('\xc2\xb9', 'sup1'), ('\xc2\xba', 'ordm'), ('\xc2\xbb', 'raquo'), ('\xc2\xbc', 'frac14'),
    ('\xc2\xbd', 'frac12'), ('\xc2\xbe', 'frac34'), ('\xc2\xbf', 'iquest'), ('\xc3\x80', 'Agrave'),
    ('\xc3\x81', 'Aacute'), ('\xc3\x82', 'Acirc'), ('\xc3\x83', 'Atilde'), ('\xc3\x84', 'Auml'),
    ('\xc3\x85', 'Aring'), ('\xc3\x86', 'AElig'), ('\xc3\x87', 'Ccedil'), ('\xc3\x88', 'Egrave'),
    ('\xc3\x89', 'Eacute'), ('\xc3\x8a', 'Ecirc'), ('\xc3\x8b', 'Euml'), ('\xc3\x8c', 'Igrave'),
    ('\xc3\x8d', 'Iacute'), ('\xc3\x8e', 'Icirc'), ('\xc3\x8f', 'Iuml'), ('\xc3\x90', 'ETH'),
    ('\xc3\x91', 'Ntilde'), ('\xc3\x92', 'Ograve'), ('\xc3\x93', 'Oacute'), ('\xc3\x94', 'Ocirc'),
    ('\xc3\x95', 'Otilde'), ('\xc3\x96', 'Ouml'), ('\xc3\x97', 'times'), ('\xc3\x98', 'Oslash'),
    ('\xc3\x99', 'Ugrave'), ('\xc3\x9a', 'Uacute'), ('\xc3\x9b', 'Ucirc'), ('\xc3\x9c', 'Uuml'),
    ('\xc3\x9d', 'Yacute'), ('\xc3\x9e', 'THORN'), ('\xc3\x9f', 'szlig'), ('\xc3\xa0', 'agrave'),
    ('\xc3\xa1', 'aacute'), ('\xc3\xa2', 'acirc'), ('\xc3\xa3', 'atilde'), ('\xc3\xa4', 'auml'),
    ('\xc3\xa5', 'aring'), ('\xc3\xa6', 'aelig'), ('\xc3\xa7', 'ccedil'), ('\xc3\xa8', 'egrave'),
    ('\xc3\xa9', 'eacute'), ('\xc3\xaa', 'ecirc'), ('\xc3\xab', 'euml'), ('\xc3\xac', 'igrave'),
    ('\xc3\xad', 'iacute'), ('\xc3\xae', 'icirc'), ('\xc3\xaf', 'iuml'), ('\xc3\xb0', 'eth'),
    ('\xc3\xb1', 'ntilde'), ('\xc3\xb2', 'ograve'), ('\xc3\xb3', 'oacute'), ('\xc3\xb4', 'ocirc'),
    ('\xc3\xb5', 'otilde'), ('\xc3\xb6', 'ouml'), ('\xc3\xb7', 'divide'), ('\xc3\xb8', 'oslash'),
    ('\xc3\xb9', 'ugrave'), ('\xc3\xba', 'uacute'), ('\xc3\xbb', 'ucirc'), ('\xc3\xbc', 'uuml'),
    ('\xc3\xbd', 'yacute'), ('\xc3\xbe', 'thorn'), ('\xc3\xbf', 'yuml'), ('\xc5\x92', 'OElig'),
    ('\xc5\x93', 'oelig'), ('\xc5\xa0', 'Scaron'), ('\xc5\xa1', 'scaron'), ('\xc5\xb8', 'Yuml'),
    ('\xc6\x92', 'fnof'), ('\xcb\x86', 'circ'), ('\xcb\x9c', 'tilde'), ('\xce\x91', 'Alpha'),
    ('\xce\x92', 'Beta'), ('\xce\x93', 'Gamma'), ('\xce\x94', 'Delta'), ('\xce\x95', 'Epsilon'),
    ('\xce\x96', 'Zeta'), ('\xce\x97', 'Eta'), ('\xce\x98', 'Theta'), ('\xce\x99', 'Iota'),
    ('\xce\x9a', 'Kappa'), ('\xce\x9b', 'Lambda'), ('\xce\x9c', 'Mu'), ('\xce\x9d', 'Nu'),
    ('\xce\x9e', 'Xi'), ('\xce\x9f', 'Omicron'), ('\xce\xa0', 'Pi'), ('\xce\xa1', 'Rho'),
    ('\xce\xa3', 'Sigma'), ('\xce\xa4', 'Tau'), ('\xce\xa5', 'Upsilon'), ('\xce\xa6', 'Phi'),
    ('\xce\xa7', 'Chi'), ('\xce\xa8', 'Psi'), ('\xce\xa9', 'Omega'), ('\xce\xb1', 'alpha'),
    ('\xce\xb2', 'beta'), ('\xce\xb3', 'gamma'), ('\xce\xb4', 'delta'), ('\xce\xb5', 'epsilon'),
    ('\xce\xb6', 'zeta'), ('\xce\xb7', 'eta'), ('\xce\xb8', 'theta'), ('\xce\xb9', 'iota'),
    ('\xce\xba', 'kappa'), ('\xce\xbb', 'lambda'), ('\xce\xbc', 'mu'), ('\xce\xbd', 'nu'),
    ('\xce\xbe', 'xi'), ('\xce\xbf', 'omicron'), ('\xcf\x80', 'pi'), ('\xcf\x81', 'rho'),
    ('\xcf\x82', 'sigmaf'), ('\xcf\x83', 'sigma'), ('\xcf\x84', 'tau'), ('\xcf\x85', 'upsilon'),
    ('\xcf\x86', 'phi'), ('\xcf\x87', 'chi'), ('\xcf\x88', 'psi'), ('\xcf\x89', 'omega'),
    ('\xcf\x91', 'thetasym'), ('\xcf\x92', 'upsih'), ('\xcf\x96', 'piv'), ('\xe2\x80\x82', 'ensp'),
    ('\xe2\x80\x83', 'emsp'), ('\xe2\x80\x89', 'thinsp'), ('\xe2\x80\x93', 'ndash'), ('\xe2\x80\x94', 'mdash'),
    ('\xe2\x80\x98', 'lsquo'), ('\xe2\x80\x99', 'rsquo'), ('\xe2\x80\x9a', 'sbquo'), ('\xe2\x80\x9c', 'ldquo'),
    ('\xe2\x80\x9d', 'rdquo'), ('\xe2\x80\x9e', 'bdquo'), ('\xe2\x80\xa0', 'dagger'), ('\xe2\x80\xa1', 'Dagger'),
    ('\xe2\x80\xa2', 'bull'), ('\xe2\x80\xa6', 'hellip'), ('\xe2\x80\xb0', 'permil'), ('\xe2\x80\xb2', 'prime'),
    ('\xe2\x80\xb3', 'Prime'), ('\xe2\x80\xb9', 'lsaquo'), ('\xe2\x80\xba', 'rsaquo'), ('\xe2\x80\xbe', 'oline'),
    ('\xe2\x81\x84', 'frasl'), ('\xe2\x82\xac', 'euro'), ('\xe2\x84\x91', 'image'), ('\xe2\x84\x98', 'weierp'),
    ('\xe2\x84\x9c', 'real'), ('\xe2\x84\xa2', 'trade'), ('\xe2\x84\xb5', 'alefsym'), ('\xe2\x86\x90', 'larr'),
    ('\xe2\x86\x91', 'uarr'), ('\xe2\x86\x92', 'rarr'), ('\xe2\x86\x93', 'darr'), ('\xe2\x86\x94', 'harr'),
    ('\xe2\x86\xb5', 'crarr'), ('\xe2\x87\x90', 'lArr'), ('\xe2\x87\x91', 'uArr'), ('\xe2\x87\x92', 'rArr'),
    ('\xe2\x87\x93', 'dArr'), ('\xe2\x87\x94', 'hArr'), ('\xe2\x88\x80', 'forall'), ('\xe2\x88\x82', 'part'),
    ('\xe2\x88\x83', 'exist'), ('\xe2\x88\x85', 'empty'), ('\xe2\x88\x87', 'nabla'), ('\xe2\x88\x88', 'isin'),
    ('\xe2\x88\x89', 'notin'), ('\xe2\x88\x8b', 'ni'), ('\xe2\x88\x8f', 'prod'), ('\xe2\x88\x91', 'sum'),
    ('\xe2\x88\x92', 'minus'), ('\xe2\x88\x97', 'lowast'), ('\xe2\x88\x9a', 'radic'), ('\xe2\x88\x9d', 'prop'),
    ('\xe2\x88\x9e', 'infin'), ('\xe2\x88\xa0', 'ang'), ('\xe2\x88\xa7', 'and'), ('\xe2\x88\xa8', 'or'),
    ('\xe2\x88\xa9', 'cap'), ('\xe2\x88\xaa', 'cup'), ('\xe2\x88\xab', 'int'), ('\xe2\x88\xb4', 'there4'),
    ('\xe2\x88\xbc', 'sim'), ('\xe2\x89\x85', 'cong'), ('\xe2\x89\x88', 'asymp'), ('\xe2\x89\xa0', 'ne'),
    ('\xe2\x89\xa1', 'equiv'), ('\xe2\x89\xa4', 'le'), ('\xe2\x89\xa5', 'ge'), ('\xe2\x8a\x82', 'sub'),
    ('\xe2\x8a\x83', 'sup'), ('\xe2\x8a\x84', 'nsub'), ('\xe2\x8a\x86', 'sube'), ('\xe2\x8a\x87', 'supe'),
    ('\xe2\x8a\x95', 'oplus'), ('\xe2\x8a\x97', 'otimes'), ('\xe2\x8a\xa5', 'perp'), ('\xe2\x8b\x85', 'sdot'),
    ('\xe2\x8c\x88', 'lceil'), ('\xe2\x8c\x89', 'rceil'), ('\xe2\x8c\x8a', 'lfloor'), ('\xe2\x8c\x8b', 'rfloor'),
    ('\xe2\x8c\xa9', 'lang'), ('\xe2\x8c\xaa', 'rang'), ('\xe2\x97\x8a', 'loz'), ('\xe2\x99\xa0', 'spades'),
    ('\xe2\x99\xa3', 'clubs'), ('\xe2\x99\xa5', 'hearts'), ('\xe2\x99\xa6', 'diams')
]

def _get_permissable(permissable):    
    return [chr(x) for x in permissable]

def _from(ds_string, silent, permissable, st):
    
    ds_string_list = list(ds_string)
    
    for i in xrange(len(ds_string_list)):
        if ds_string_list[i] not in permissable:
            if silent and isinstance(silent, str):
                ds_string_list[i] = silent
            elif silent:
                ds_string_list[i] = '_'
            else: 
                raise ValueError(SS_ERROR % (st, repr(ds_string[i])))
            
    return "".join(ds_string_list)    
    

def ss_from_ds(ds_string, silent=False):
    """
    A simple string is a string whose content bytes
    must be in a limited set of bytes.
    
    simple_strings can contain:
        A-Z, a-z, 0-9, safe specials.
        
    """
    ss_permissable = [chr(x) for x in SS_PERMISSABLE]
    return _from(ds_string, silent, ss_permissable, "Simple")
    

def cs_from_ds(ds_string, silent=False):
    """
    A complex string can have all the characters of a
    simple string + '[]/\|_-' this is pretty rigerous
    """
    cs_permissable = _get_permissable(CS_PERMISSABLE)
    return _from(ds_string, silent, cs_permissable, "Complex")

#def em_from_ds(ds_string):
    # After research this needs some serious work.
    #"""
    #An email string, can have any character legal in an
    #email address. So, lowers, uppers, 0-9 and .'s
    #"""
    #em_permissable = _get_permissable(EM_PERMISSABLE)
    #return _from(ds_string, False, em_permissable, "Email")
    
def hs_from_ds(ds_string, silent=False):
    """
    Convert a dangerous string into an html string.
    """
    amp = "__amp%samp__" % random.randint(100000, 10000000)
    semi = "__semi%ssemi__" % random.randint(100000, 10000000)
    for symbol, entity in SE_TBL:
        if symbol in ds_string:
            ds_string = ds_string.replace(symbol, "%s%s%s" % (amp, entity, semi))
            
    hs_string = ds_string.replace(amp,'&').replace(semi, ';')
    return hs_string
    
        
    
    
    
    
        
        
        
        
    
        
        
        
    
    

