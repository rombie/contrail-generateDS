#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#

import logging

from ifmap_global import getCppType, getJavaType, IsGeneratedType, CamelCase

def CppVariableName(varname):
    keywords = ['static']
    if varname in keywords:
        varname = '_' + varname;
    return varname
        
class MemberInfo(object):
    def __init__(self):
        self.ctypename = ''
        self.jtypename = ''
        self.membername = ''
        self.isSequence = False
        self.isComplex = False
        self.xsd_object = None
        self.sequenceType = None

class ComplexType(object):
    def __init__(self, name):
        self._name = name
        self._data_types = []
        self._data_members = []

    def getName(self):
        return self._name

    def getDependentTypes(self):
        return self._data_types

    def getDataMembers(self):
        return self._data_members

    def Build(self, xsdTypeDict, cTypeDict):
        self._xsd_type = xsdTypeDict[self._name]

        children = self._xsd_type.getChildren()
        for child in children:
            if child.isComplex():
                descendent = ComplexTypeLocate(xsdTypeDict, cTypeDict, child.getType())
                self._data_types.append(descendent)
                cpptype = child.getType()
                jtype = child.getType()
                cppname = child.getCleanName()
            else:
                cpptype = getCppType(child.getType())
                jtype = getJavaType(child.getType())
                if cpptype == 'void':
                    logger = logging.getLogger('type_model')
                    logger.warning('simpleType %s: unknown' % child.getType())
                cppname = child.getCleanName()

            member = MemberInfo()
            member.elementname = child.getName()
            member.membername = CppVariableName(cppname)
            member.xsd_object = child
            member.isComplex = child.isComplex()
            if child.getMaxOccurs() > 1:
                member.membername = cppname# + '_list'
                member.sequenceType = cpptype
                cpptype = 'std::vector<%s>' % cpptype
                jtype = 'List<%s>' % jtype
                member.isSequence = True

            member.ctypename = cpptype
            member.jtypename = jtype
            self._data_members.append(member)


def ComplexTypeLocate(xsdTypeDict, cTypeDict, xtypename):
    if xtypename in cTypeDict:
        return cTypeDict[xtypename]

    if not xtypename in xsdTypeDict:
        logger = logging.getLogger('type_model')
        logger.warning('%s not found in type dictionary', xtypename)
        return None

    ctype = ComplexType(xtypename)
    ctype.Build(xsdTypeDict, cTypeDict)
    cTypeDict[xtypename] = ctype
    return ctype
