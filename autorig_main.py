import maya.cmds as cmds 
import math 


## Util functions


def getWSRotate(obj):
    rotate = cmds.xform(obj, q = True, ws = True, ro = True)
    return rotate
    
def getWSTranslate(obj):
    translate = cmds.xform(obj, q = True, ws = True, t = True)
    return translate


def getVectorMinus(va, vb):
    return (va[0] - vb[0], va[1] - vb[1], va[2] - vb[2])
    
def getWRPivot(obj):
    wrp = cmds.xform(obj, q = True, ws = True, rp = True)
    return wrp

# utils for getting frequently used attr
def GetRootScale():
    return cmds.getAttr(centralCTRL['rootCtrl']+'.scaleX')

# check if attr exists 
def CheckAttributeExists(nodename, attrname):
    attrExist = cmds.attributeQuery(attrname, node=nodename, exists=True)    
    return attrExist
    
# check if node exists 
def CheckObjExists(obj):
    search = cmds.ls(obj)
    if search is None or len(search) == 0 :    
        return (False, None)
    else: 
        return (True, search[0])
        
# check if connection exists on nodes and clean up unitconversion nodes
def CleanConnectionOnNode(nodename, attrname, isinput):
    if input:
        # check if anything is connected to the attr
        conn = cmds.listConnections(nodename+'.'+attrname, s=True, p = True, d = False)
        if conn is None or len(conn) == 0:
            print('not connected')
            return 0 
        else:
            cmds.disconnectAttr(conn[0], nodename+'.'+attrname)
            if 'unitConversion' in conn[0]:
                print('[Node deleted for cleanup]' + conn[0])
                cmds.delete(conn[0])
                
    else:
        # check if anything is taking the attr as the source
        conn = cmds.listConnections(nodename+'.'+attrname, s=False, p = True, d = True)
        if conn is None or len(conn) == 0:
            print('not connected')
            return 0 
        else:
            cmds.disconnectAttr(nodename+'.'+attrname, conn[0])
            if 'unitConversion' in conn[0]:
                print('[Node deleted for cleanup]' + conn[0])
                cmds.delete(conn[0])
    
    #conn = cmds.listConnections(nodename+'.'+attrname, c=True, p = True)
    #if conn is None or len(conn) == 0:
    #    print('not connected')
    #    return 0 
    #else:
    #    print(conn)
    #    if isinput:
    #        cmds.disconnectAttr(conn[1], conn[0])
    #    else:
    #        cmds.disconnectAttr(conn[0], conn[1])
    #    if 'unitConversion' in conn[1]:
    #        print('[Node deleted for cleanup]' + conn[1].split('.')[0])
    #        cmds.delete(conn[1].split('.')[0])           
        
    return 0   
    
## Util: hide all locators in the rig group 
def HideAllLocators():
    return 0
    
    

# vars for general settings 
gSceneScale = 20.0  # scale for your scene/ model


#var 
lGimbleControl = 'arm_l_GIMBLE_CTRL'
lArmIKFKSwitch = 'LEFT_arm_IKFK_SWITCH'

lArmIKCTRL = 'arm_l_IK_CTRL'
lArmIKCTRLSnap = 'arm_l_IK_CTRL_snap_GRP'
# get the default grp world pivot 
lArmIKCTRLDefault = 'arm_l_IK_CTRL_default_GRP'


lElbowCTRLSnap = 'elbow_l_snap_GRP'
lElbowCTRL = 'elbow_l_PV_CTRL'
#because the elbow & arm Ik ctrls pivots are reseted, need to use this method to change the value
lElbowCTRLDefault = 'elbow_l_PV_CTRL_default_GRP'
lElbowOffset = 'elbow_l_offset_GRP'


lUpperarmResult = 'upperarm_l_JNT_snap'
lUpperarmFK = 'upperarm_l_FK_JNT'
lUpperarmIK = 'upperarm_l_IK_JNT'


lLowerarmResult = 'lowerarm_l_JNT_snap'
lLowerarmFK = 'lowerarm_l_FK_JNT'
lLowerarmIK = 'lowerarm_l_IK_JNT'


lWristResult = 'wrist_l_JNT_snap'
lWristFK = 'wrist_l_FK_JNT'
lWristIK = 'wrist_l_IK_JNT'



def lArmMatchFK2IK():
    
    # set rot of FK to match result joints in IK mode, TODO what if under different translation space? is the snap jnt necessary?
    cmds.xform(lUpperarmFK, ro = getWSRotate(lUpperarmResult), ws = True)
    cmds.xform(lLowerarmFK, ro = getWSRotate(lLowerarmResult), ws = True)
    cmds.xform(lWristFK, ro = getWSRotate(lWristResult), ws = True)
    
    #match arm length 
    
    
    
    #reset gimble correction node 
    cmds.xform(lGimbleControl, ro = (0,0,0))
    
    #mod attributes on the left arm 
    cmds.setAttr(lArmIKFKSwitch + '.FKIK_blend', 0)
    
#left arm switch to IK 

def lArmMatchIK2FK():
    
    cmds.xform(lArmIKCTRL, ro = getWSRotate(lArmIKCTRLSnap), ws = True)
    print(getWRPivot(lArmIKCTRLSnap))
    temp = getVectorMinus(getWRPivot(lArmIKCTRLSnap) , getWRPivot(lArmIKCTRLDefault))
    cmds.xform(lArmIKCTRL, t = temp, ws = True)
    
    temp = getVectorMinus(getWRPivot(lElbowCTRLSnap),getWRPivot(lElbowCTRLDefault))
    #temp = getVectorMinus(temp, lElbowInitialOffset)
    cmds.xform(lElbowCTRL, t = temp, ws = True)
    
    #print(getWSTranslate(lWristResult))
    
    
    #upperarm rot ?
    
    cmds.xform(lUpperarmIK, ro = getWSRotate(lUpperarmResult), ws = True)
    
    cmds.setAttr(lArmIKFKSwitch + '.FKIK_blend', 1)
    
    
#arm chain 
armResultJNT = {}
armIKJNT = {}
armFKJNT = {}
armCTRL = {}
armStat = {}
armGRP = {}
armHDL = {}
# for generate rig gr
armRigGroup = {'r_rigGRP':{}, 'l_rigGRP':{}}

# central: head&neck, body, root
centralCTRL = {}
    
    

#Initialize joint names
#TODO: add verification steps 
def ArmInitJointNames(isRight):
    #traverse ans assign joint names to vars 
    #TODO add name checks
    print("Init names")
    
    ## Central ##
    global centralCTRL
    centralCTRL = {'rootCtrl':'Root_transform_CTRL'}
    
    global partSpaceGRP
    partSpaceGRP = {'root':'Root_transform_CTRL', 'body':'torso_rig_GRP', 'shoulder':'shoulder_bind_JNT', 'pelvis':'pelvis_bind_JNT'}
    
    
    ## Arms ## 
    # Note: for result, ik and fk jnt, the entry for dictionary is the same for later fuctionality (blend all three types of jnts)
    global armHDL
    armHDL = {'r_armHDL' : 'arm_r_IK_HDL', 'r_handHDL':'hand_r_IK_HDL'}
    
    global armGRP
    armGRP = {'r_HDLConstGRP':'arm_r_HDLConst_GRP', 'r_IKConstGRP':'arm_r_IKConst_GRP', 'r_FKConstGRP':'arm_r_FKConst_GRP', 'r_ResultConstGRP':'arm_r_resultConst_GRP'}
    global armStat
    armStat = {'r_upperarmIKLength': 0, 'r_lowerarmIKLength':0, 'r_lowerarmTranslateX': 0, 'r_wristTranslateX': 0 }
    global armCTRL
    armCTRL = {'l_armSwitchCtrl':'LEFT_arm_IKFK_SWITCH', 'r_armSwitchCtrl':'RIGHT_arm_IKFK_SWITCH', 'r_gimbleCtrl' : 'arm_r_GIMBLE_CTRL',
                'r_upperarmCtrl':'upperarm_r_FK_JNT', 'r_lowerarmCtrl': 'lowerarm_r_FK_JNT', 'r_wristCtrl': 'wrist_r_FK_JNT',
                'r_armIKCtrl':'r_arm_IK_CTRL', 'r_elbowIKLOC': 'r_elbow_LOC','r_elbowIKCtrl': 'r_elbow_PV_CTRL', 'r_elbowFK_lowerarm':'elbow_lowerarm_r_FK_JNT','r_elbowFK_wrist':'elbow_wrist_r_FK_JNT', 'r_elbowFK_hand':'elbow_hand_r_FK_JNT' }
  
    global armResultJNT 
    armResultJNT = {'r_UpperArm': 'upperarm_r_JNT', 'r_LowerArm': 'lowerarm_r_JNT', 'r_Wrist': 'wrist_r_JNT', 'r_Hand' : 'hand_r_JNT',
                    'l_UpperArm': 'upperarm_l_JNT', 'l_LowerArm': 'lowerarm_l_JNT', 'l_Wrist': 'wrist_l_JNT', 'l_Hand' : 'hand_l_JNT'}
    global armIKJNT 
    armIKJNT = {'r_UpperArm': 'upperarm_r_IK_JNT', 'r_LowerArm': 'lowerarm_r_IK_JNT', 'r_Wrist': 'wrist_r_IK_JNT', 'r_Hand' : 'hand_r_IK_JNT',
                'l_UpperArm': 'upperarm_l_IK_JNT', 'l_LowerArm': 'lowerarm_l_IK_JNT', 'l_Wrist': 'wrist_l_IK_JNT', 'l_Hand' : 'hand_r_IK_JNT'}
    global armFKJNT 
    armFKJNT = {'r_UpperArm': 'upperarm_r_FK_JNT', 'r_LowerArm': 'lowerarm_r_FK_JNT', 'r_Wrist': 'wrist_r_FK_JNT', 'r_Hand' : 'hand_r_FK_JNT',
                'l_UpperArm': 'upperarm_l_FK_JNT', 'l_LowerArm': 'lowerarm_l_FK_JNT', 'l_Wrist': 'wrist_l_FK_JNT', 'l_Hand' : 'hand_l_FK_JNT'}
    
    
    #init global length values
    translateX = cmds.getAttr(armResultJNT['r_LowerArm']+'.translateX')
    armStat['r_lowerarmTranslateX'] = translateX
    translateX = cmds.getAttr(armResultJNT['r_Wrist']+'.translateX')
    armStat['r_wristTranslateX'] = translateX
    
    return 1
    
## add objs to rig group 
   

    
# attach proxy mesh 
def CreateProxyMeshGRP(jntName):
    grpName = jntName+'_ProxyGEO_GRP'
    grpSearch = cmds.ls(grpName)
    
    # TODO: need to align the group rot x axis with the coresponding joint local x
    if grpSearch == None or len(grpSearch) is 0: 
        print("Create proxy group")
        grp = cmds.group(n = grpName, p = armResultJNT[jntName], em = True)
        print(grp)
        #cmds.manipPivot(grp, p = getWSTranslate(armResultJNT[jntName]))
    else:
        print("GRP already exists")
        #link the result jnt translate X val with the proxy geoGRP
        
        
    return 0
    
# setting up result arm for rigging 
# create empty grp node for each result joint as the slot for the proxy mesh         
def ConfigResultArm(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
        print('Create empty grps for proxy mesh')
        for jn in armResultJNT:
            print(jn) 
            if prefix in jn:
                CreateProxyMeshGRP(jn)
                
    # link procy grp scaleX with jnt translate X 
    # upperarm stretch
    proxyGRP = prefix+'UpperArm_ProxyGEO_GRP'
   
    
    nodename = prefix + 'UpperArm_Stretch_DefaultLengthDiv'
    exists, defaultLengthDiv = CheckObjExists(nodename)
    print(defaultLengthDiv)
    if not exists:
        defaultLengthDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    cmds.setAttr(defaultLengthDiv+'.operation', 2)
    CleanConnectionOnNode(defaultLengthDiv, 'input1X', True)
    cmds.connectAttr(armResultJNT[prefix+'LowerArm']+ '.translateX', defaultLengthDiv + '.input1X', )
    CleanConnectionOnNode(defaultLengthDiv, 'input2X', True)
    print (armStat[prefix+'lowerarmTranslateX'])
    cmds.setAttr(defaultLengthDiv + '.input2X', armStat[prefix+'lowerarmTranslateX'])
    CleanConnectionOnNode(defaultLengthDiv, 'outputX', False)
    CleanConnectionOnNode(proxyGRP, 'scaleX', True)
    cmds.connectAttr(defaultLengthDiv+'.outputX', proxyGRP + '.scaleX')
    
    
    # lowerarm stretch
    proxyGRP = prefix+'LowerArm_ProxyGEO_GRP'
    
    nodename = prefix + 'LowerArm_Stretch_DefaultLengthDiv'
    exists, defaultLengthDiv = CheckObjExists(nodename)
    print(defaultLengthDiv)
    if not exists:
        defaultLengthDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    cmds.setAttr(defaultLengthDiv+'.operation', 2)
    CleanConnectionOnNode(defaultLengthDiv, 'input1X', True)
    cmds.connectAttr(armResultJNT[prefix+'Wrist']+ '.translateX', defaultLengthDiv + '.input1X', )
    CleanConnectionOnNode(defaultLengthDiv, 'input2X', True)
    cmds.setAttr(defaultLengthDiv + '.input2X', armStat[prefix+'wristTranslateX'])
    CleanConnectionOnNode(defaultLengthDiv, 'outputX', False)
    CleanConnectionOnNode(proxyGRP, 'scaleX', True)
    cmds.connectAttr(defaultLengthDiv+'.outputX', proxyGRP + '.scaleX')
        
    return 1
    
#create ctrl curves and attach to FK arm jnt
#create gimble correction grp 
#check naming conventions & attach ctrls 
def CreateContorlCurvesAndParentTo(jnt, jntchain, normal):
    # TODO: adding a force flag to clean the jnt & Error handling 
    if normal is None:
        normal = (0,0,1)
    crvname = jnt+'_curve'
    #check if joint already has a curveshape
    jntshape = cmds.listRelatives(jntchain[jnt], shapes=True)
    if jntshape is None or len(jntshape) == 0:
    
        crvsearch = cmds.ls(crvname)
        if crvsearch is not None and len(crvsearch) > 0:
            cmds.delete(crv)   
            
        crv = cmds.circle(n = crvname, r = gSceneScale, nr = normal)
        crvshape = cmds.listRelatives(crv, shapes=True)[0]
        cmds.parent(crvshape, jntchain[jnt], r = True, s = True)
        cmds.delete(crv)
            
    else:
        #TODO change to better warning msg
        print("FK ARM already has a contorl curve, skip setting up this joint")
        return 0
    

def ConfigureFKArm(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
        controlPrefix = 'RIGHT_'
    else: 
        prefix = 'l_'
        controlPrefix = 'LEFT_'
    
    
    print('Create empty grps for proxy mesh')
    for jn in armFKJNT:
        print(jn) 
        if (prefix in jn) and (not '_Hand' in jn):
            # create control curves and attach to the joint 
            CreateContorlCurvesAndParentTo(jn, armFKJNT, (0,1,0))
            # link ctrls visibility with fkik switch 
            
            cmds.delete(armFKJNT[jn], at = 'visibility', e = True)
            expstring = "if({cPrefix}arm_IKFK_SWITCH.FKIK_blend == 1){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(cPrefix = controlPrefix, jname = armFKJNT[jn])
            print(expstring)
            
            name = jn + 'FKIKVisibility_expression'
            cmds.expression(o = armFKJNT[jn], s = expstring, ae = True, n = name)
        #end prefix check 
    #end setup for each joint    
    
    print('## setting up FK ARM stretch & squash')
    #adding stretch&squash function to FK arm joint
    nname = armCTRL[prefix+'upperarmCtrl']
    attr = 'length'
    translateX = armStat[prefix+'lowerarmTranslateX']
    if not CheckAttributeExists(nname, attr):
        print('## Create length attr for ctrl')
        cmds.addAttr(nname, ln = attr, at = 'float', nn = 'Length', k = True)
        #check if there is a key on the attribute 
    
    animNode = 'lowerarm_' + prefix + 'FK_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve")
        cmds.setDrivenKeyframe(armFKJNT[prefix+'LowerArm'], attribute='translateX', currentDriver = nname+'.length', driverValue = 0, value = 0)
        cmds.setDrivenKeyframe(armFKJNT[prefix+'LowerArm'], attribute='translateX', currentDriver = nname+'.length', driverValue = 1, value = translateX)
        cmds.setAttr(nname+'.'+attr, 1)
        # update the animation curve 
        cmds.keyTangent(armFKJNT[prefix+'LowerArm'], attribute='translateX', itt = 'spline', ott = 'spline')
        cmds.setInfinity(armFKJNT[prefix+'LowerArm']+'.translateX', poi = 'linear')
          
    
    
    nname = armCTRL[prefix+'lowerarmCtrl']
    attr = 'length'
    translateX = armStat[prefix+'wristTranslateX']
    if not CheckAttributeExists(nname, attr):
        print('## Create length attr for ctrl')
        cmds.addAttr(nname, ln = attr, at = 'float', nn = 'Length', k = True)
        #check if there is a key on the attribute 
        
    animNode = 'wrist_' + prefix + 'FK_JNT_translateX'
    print(animNode)
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ('create new curve')
        cmds.setDrivenKeyframe(armFKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = nname+'.length', driverValue = 0, value = 0) 
        cmds.setDrivenKeyframe(armFKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = nname+'.length', driverValue = 1, value = translateX)
        cmds.setAttr(nname+'.'+attr, 1)
        cmds.keyTangent(armFKJNT[prefix+'LowerArm'], attribute='translateX', itt = 'spline', ott = 'spline')
        cmds.setInfinity(armFKJNT[prefix+'LowerArm']+'.translateX', poi = 'linear')
    else:
        print('wrist r fk anim curve already exists, skip creation')
    
    

    print("##[FINISHED] stretch & squash arm setup success!")
        
    
    #end right arm config         
    
    return 1
    
 
#setup arm ik, hand ik, arm pole vector 
#attach ctrl 
def ConfigureIKArm(isRight):
    # TODO: make sure this step runs after the FK setup
    #      set up stretch & squash 

    prefix = ''
    if isRight:
        prefix = 'r_' 
        contorlPrefix = 'RIGHT_'
    else:
        prefix = 'l_'
        contorlPrefix = 'LEFT_'
    
  
    ##
    ## arm IK basic set up
    ##
    
    #add elbow contorl 
    elbowCtrl = armCTRL[prefix+'elbowIKCtrl']
    elbowLoc = armCTRL[prefix+'elbowIKLOC']
    attr = 'elbow_snap'
    if not CheckAttributeExists(elbowCtrl, attr):
        cmds.addAttr(elbowCtrl, ln = attr, at = 'float', min = 0, max = 1, k = True, nn = 'Elbow Snap')
    attr = 'elbow_fkik_blend'
    if not CheckAttributeExists(elbowCtrl, attr):
        cmds.addAttr(elbowCtrl, ln = attr, at = 'float', min = 0, max = 1, k = True, nn = 'Elbow FK/IK Blend')
        
    #duplicate IK ctrl from lowerarm to hand , rename with elnow prefix 
    #parent under the elbowCtrl, move to the same location 
    
    exists, elbowLowerarm = CheckObjExists(armCTRL[prefix+'elbowFK_'+'hand'])
    elbowChain = []
    if not exists:
        elbowLowerarm = cmds.duplicate(armFKJNT[prefix+'LowerArm'], ic = False, rc = True)
        for e in elbowLowerarm:
            name = e.split(prefix + 'FK_JNT')
            newname = 'elbow_' + name[0] + prefix + 'FK_JNT'
            en = cmds.rename(e, newname)
            elbowChain.append(en)
    else:
        print("Elbow fk chain exists , skip creation ")
        elbowLowerarm = cmds.ls(armCTRL[prefix+'elbowFK_'+'lowerarm'])
        elbowChain.append(elbowLowerarm)
    
    # reparent the chain 
    print(elbowChain[0])
    if not cmds.listRelatives(elbowChain[0], p = True)[0] == elbowCtrl:
        cmds.parent(elbowChain[0], elbowCtrl)
    pos = getWSTranslate(elbowLoc)
    cmds.xform(elbowChain[0], ws = True, t = pos)
    
    
    ##
    ## Elbow FKIK hybrid control solution  
    ##
    
    # set up parent constraint on arm_ctrl, elbowFK_wrist, and the arm_HDLConst_GRP 
    # TODO: need to make sure the ik ctrl, grp and wrist joint has the same local axis
    IKConstGRP = armGRP[prefix+'HDLConstGRP']
    targets = []
    targets.append(armCTRL[prefix+'armIKCtrl'])
    targets.append(armCTRL[prefix+'elbowFK_wrist'])
    constraint = cmds.parentConstraint(targets, IKConstGRP)[0]
    print (constraint)
    
    attr = armCTRL[prefix+'armIKCtrl']+'W0'
    cmds.delete(constraint, at = attr, e = True)
    expstring = "{objname}.{attrname} = {elbow}.elbow_fkik_blend".format(elbow = armCTRL[prefix+'elbowIKCtrl'], attrname = attr, objname = constraint)
    print(expstring)
    cmds.expression(o = constraint, s = expstring, ae = True)
    
    attr = armCTRL[prefix+'elbowFK_wrist']+'W1'
    cmds.delete(constraint, at = attr, e = True)
    expstring = "{objname}.{attrname} = 1-{elbow}.elbow_fkik_blend".format(elbow = armCTRL[prefix+'elbowIKCtrl'], attrname = attr, objname = constraint)
    print(expstring)
    cmds.expression(o = constraint, s = expstring, ae = True)
    #set the elbow_fkik_blend to 1: set to the ik controller
    cmds.setAttr(armCTRL[prefix+'elbowIKCtrl']+'.elbow_fkik_blend', 1)
          
    #set up contorller visibility
    #arm controller
    visContorl = armCTRL[prefix+'armIKCtrl']
    cmds.delete(visContorl, at = 'visibility', e = True)
    expstring = "if({cprefix}arm_IKFK_SWITCH.FKIK_blend == 0 || {elbow}.elbow_fkik_blend <= 0.01){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(elbow = armCTRL[prefix+'elbowIKCtrl'], jname = visContorl, cprefix = contorlPrefix)
    #print(expstring)
    cmds.expression(o = visContorl, s = expstring, ae = True)     
    
    # elbow controller
    visContorl = ''
    visContorl = armCTRL[prefix+'elbowIKCtrl']
    print(visContorl)
    cmds.delete(visContorl, at = 'visibility', e = True)
    expstring = "if({cprefix}arm_IKFK_SWITCH.FKIK_blend == 0){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(jname = visContorl, cprefix = contorlPrefix)
    print(expstring)
    cmds.expression(o = visContorl, s = expstring, ae = True) 
    
    
    # elbow FK contorllers
    visContorl = ''
    visContorl = armCTRL[prefix+'elbowFK_'+'lowerarm']
    print(visContorl)
    cmds.delete(visContorl, at = 'visibility', e = True)
    expstring = "if({cprefix}arm_IKFK_SWITCH.FKIK_blend == 0 || {elbow}.elbow_fkik_blend >= 0.99){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(elbow = armCTRL[prefix+'elbowIKCtrl'], jname = visContorl, cprefix = contorlPrefix)
    print(expstring)
    cmds.expression(o = visContorl, s = expstring, ae = True) 
    
    
    ## 
    ## Create FKIK snap loators
    ## - copy paste to FK grps 
    
    
    ##
    ## Stretch & Squash
    ##
    
    # stretch with IK arm control solver
    # total distance 
    
    print('## set up stretch and squash for IK arm')
    # create locator at the ik wrist
    locName = prefix+"wristLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(armIKJNT[prefix+'Wrist']), a = True) 
    #cmds.xform(locNode, ws = True, t = getWSTranslate(armIKJNT[prefix+'Wrist']))
         
    if cmds.listRelatives(locNode, p = True) == None or not cmds.listRelatives(locNode, p = True)[0] == IKConstGRP:
        cmds.parent(locNode, IKConstGRP)
        
    
    WristLocShape = cmds.listRelatives(locNode, shapes=True)[0]
 
    
    # create locator at the IK upperarm JNT
    locName = prefix+"upperarmLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(armIKJNT[prefix+'UpperArm']), a = True) 
    #cmds.xform(locNode, ws = True, t = getWSTranslate(armIKJNT[prefix+'UpperArm']))
        
    if cmds.listRelatives(locNode, p = True) == None or not cmds.listRelatives(locNode, p = True)[0] == armIKJNT[prefix+'UpperArm']:
        cmds.parent(locNode, armIKJNT[prefix+'UpperArm'])
        
     
    
    
    UpperarmLocShape = cmds.listRelatives(locNode, shapes=True)[0]
 
    
    distName = prefix+"armIKTotalLength"
    exists, totalDistNode = CheckObjExists(distName)
    if not exists:
        totalDistNode = cmds.createNode('distanceDimShape', n = distName)   
        
    print (totalDistNode)
    
    pnode = cmds.listRelatives(totalDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, distName+'_Measure', ignoreShape = True)
    
     
    p1 = WristLocShape
    p2 = UpperarmLocShape
    CleanConnectionOnNode(totalDistNode, 'startPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', totalDistNode + '.startPoint')
    CleanConnectionOnNode(totalDistNode, 'endPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', totalDistNode + '.endPoint')
    defaultDistance = cmds.getAttr(totalDistNode+'.distance')
    
    
    print(defaultDistance)
    animNode = 'wrist_' + prefix + 'IK_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve")
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = armStat[prefix+'wristTranslateX']) 
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = armStat[prefix+'wristTranslateX']*2)
        cmds.keyTangent(armIKJNT[prefix+'Wrist'], attribute='translateX', itt = 'spline', ott = 'spline')
        cmds.setInfinity(armIKJNT[prefix+'Wrist']+'.translateX', poi = 'linear')
    else:
        print ("Animation Curve Already exists")
    animNode = 'lowerarm_' + prefix + 'IK_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        cmds.setDrivenKeyframe(armIKJNT[prefix+'LowerArm'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = armStat[prefix+'lowerarmTranslateX']) 
        cmds.setDrivenKeyframe(armIKJNT[prefix+'LowerArm'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = armStat[prefix+'lowerarmTranslateX']*2)
        cmds.keyTangent(armIKJNT[prefix+'LowerArm'], attribute='translateX', itt = 'spline', ott = 'spline')
        cmds.setInfinity(armIKJNT[prefix+'LowerArm']+'.translateX', poi = 'linear')
   
   
        
    ## counter rootScale effect
    nodename = prefix + 'IKUpperArm_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'lowerarm_' + prefix + 'IK_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    #CleanConnectionOnNode(armFKJNT[prefix+'LowerArm'], 'translateX', False)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')
    
    
    nodename = prefix + 'IKLowerArm_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'wrist_' + prefix + 'IK_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    #CleanConnectionOnNode(armFKJNT[prefix+'LowerArm'], 'translateX', False)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')
    
   
    ##  Elbow snap set up 
    # distance from elbow to upperarm
    distName = prefix+"armElbowToUpperarmLength"
    exists, upperDistNode = CheckObjExists(distName)
    if not exists:
        upperDistNode = cmds.createNode('distanceDimShape', n = distName)     
    p1 = armCTRL[prefix+'elbowIKLOC']
    p2 = UpperarmLocShape
    CleanConnectionOnNode(upperDistNode, 'startPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', upperDistNode + '.startPoint')
    CleanConnectionOnNode(upperDistNode, 'endPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', upperDistNode + '.endPoint')
    pnode = cmds.listRelatives(upperDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, distName+'_Measure', ignoreShape = True)
    
    
    # distance from elbow to wrist
    distName = prefix+"armElbowToWristLength"
    exists, wristDistNode = CheckObjExists(distName)
    if not exists:
        wristDistNode = cmds.createNode('distanceDimShape', n = distName)     
    p1 = armCTRL[prefix+'elbowIKLOC']
    p2 = WristLocShape
    CleanConnectionOnNode(wristDistNode, 'startPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', wristDistNode + '.startPoint')
    CleanConnectionOnNode(wristDistNode, 'endPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', wristDistNode + '.endPoint')
    pnode = cmds.listRelatives(wristDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, distName+'_Measure', ignoreShape = True)
    
    # default turn off the elbow snap
    cmds.setAttr(armCTRL[prefix+'elbowIKCtrl']+ '.elbow_snap', 0)
    
    divName = 'elbow_'+prefix+'FKIKUpperarmRootscaleDiv'
    exists,divNode = CheckObjExists(divName)
    if not exists:
        divNode = cmds.createNode('multiplyDivide', n = divName)
    cmds.setAttr(divNode+'.operation', 2)
    CleanConnectionOnNode(divNode, 'input1X', True)
    cmds.connectAttr(upperDistNode+'.distance', divNode+'.input1X')
    CleanConnectionOnNode(divNode, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', divNode+'.input2X')

    
    animNode = 'lowerarm_' + prefix + 'IK_JNT_translateX'
    nodeName = prefix+"upperarmElbowFKIK_Choice"
    exists,blendNode = CheckObjExists(nodeName)
    if not exists:
        blendNode = cmds.createNode('blendColors', n = nodeName)
    CleanConnectionOnNode(divNode, 'outputX', False)
    CleanConnectionOnNode(blendNode, 'blender', True)
    cmds.connectAttr(armCTRL[prefix+'elbowIKCtrl']+ '.elbow_snap', blendNode + '.blender')
    CleanConnectionOnNode(blendNode, 'color1R', True)
    cmds.connectAttr(divNode+'.outputX', blendNode + '.color1R')
    CleanConnectionOnNode(blendNode, 'color2R', True)
    cmds.connectAttr(animNode+'.output', blendNode + '.color2R')
    
    CleanConnectionOnNode(armIKJNT[prefix+'LowerArm'], 'translateX', True)
    cmds.connectAttr(blendNode+'.outputR', armIKJNT[prefix+'LowerArm'] + '.translateX')
    
    
    
    divName = 'elbow_'+prefix+'FKIKLowerarmRootscaleDiv'
    exists,divNode = CheckObjExists(divName)
    if not exists:
        divNode = cmds.createNode('multiplyDivide', n = divName)
    cmds.setAttr(divNode+'.operation', 2)
    CleanConnectionOnNode(divNode, 'input1X', True)
    cmds.connectAttr(wristDistNode+'.distance', divNode+'.input1X')
    CleanConnectionOnNode(divNode, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', divNode+'.input2X')
    
    
    animNode = 'wrist_' + prefix + 'IK_JNT_translateX'
    nodeName = prefix+"lowerarmElbowFKIK_Choice"
    exists,blendNode = CheckObjExists(nodeName)
    if not exists:
        blendNode = cmds.createNode('blendColors', n = nodeName)
    CleanConnectionOnNode(divNode, 'outputX', False)
    CleanConnectionOnNode(blendNode, 'blender', True)
    cmds.connectAttr(armCTRL[prefix+'elbowIKCtrl']+ '.elbow_snap', blendNode + '.blender')
    CleanConnectionOnNode(blendNode, 'color1R', True)
    cmds.connectAttr(divNode+'.outputX', blendNode + '.color1R')
    CleanConnectionOnNode(blendNode, 'color2R', True)
    cmds.connectAttr(animNode+'.output', blendNode + '.color2R')
    
    CleanConnectionOnNode(armIKJNT[prefix+'Wrist'], 'translateX', True)
    cmds.connectAttr(blendNode+'.outputR', armIKJNT[prefix+'Wrist'] + '.translateX')
    
     
    
    # stretch with elbow FK -- TODO:? seems to be handled as elbow fk drives the ik bone 
    
    
    
   
    
    return 0


# FKIK setup module
# link corresponding ik fk joint to result jnt 
# link the switch control blend attr with colorblender.blender attr    
def CreateFKIKBlendForJoint(jntName, ctrlName):
    # TODO: clean up code to adapt to both arms & legs 
     
    print('## [FKIK blend setup] :' + jntName)
    
    rj = armResultJNT[jntName]
    fj = armFKJNT[jntName]
    ij = armIKJNT[jntName]
    
    
    
    #find the controller
    tempname = armCTRL[ctrlName]
    switchSearch = cmds.ls(tempname)   #TODO change this to a pram for leg and arm
    if switchSearch is None or len(switchSearch) > 1:
        # TODO change this to a proper warning/error msg
        print("[ERROR] please double check if the switch ctrl exists, end rigging process")
        return 0
    else:
        switchCtrl = switchSearch[0]
        print(switchCtrl)
    
    switchAttr = 'FKIK_blend'
    attrExist = cmds.attributeQuery(switchAttr, node=switchCtrl, exists=True)
    
    if not attrExist:
        cmds.addAttr(switchCtrl, ln = switchAttr, at = 'float', max = 1, min = 0, nn = 'FK/IK Blend', k = True)
    #set up connection graph for the elbow blend
        
                
    
    # create blend node for rotation 
    nodeNameRot = jntName + '_FKIKBlend_Rot'
    nsearch = cmds.ls(nodeNameRot)
    if len(nsearch) is 0:    
        nrot = cmds.createNode('blendColors', n = nodeNameRot)
    else: 
        nrot = nsearch[0] 
        
        
    #break connection if it exists
    CleanConnectionOnNode(nodeNameRot, 'color1', True)
    cmds.connectAttr(ij + '.rotate', nodeNameRot + '.color1')
    
    CleanConnectionOnNode(nodeNameRot, 'color2', True)
    cmds.connectAttr(fj + '.rotate', nodeNameRot + '.color2')
    
    CleanConnectionOnNode(nodeNameRot, 'output', False)
    cmds.connectAttr(nodeNameRot + '.output', rj + '.rotate')
    
    CleanConnectionOnNode(nodeNameRot, 'blender', True)
    cmds.connectAttr(switchCtrl+'.'+switchAttr, nodeNameRot + '.blender')
    
    
    #create blend node for translate
    nodeNameTran = jntName + '_FKIKBlend_Tran'
    nsearch = cmds.ls(nodeNameTran)
    if len(nsearch) is 0:    
        ntran = cmds.createNode('blendColors', n = nodeNameTran)
    else: 
        ntran = nsearch[0] 
    
    CleanConnectionOnNode(nodeNameTran, 'color1', True)    
    cmds.connectAttr(ij + '.translate', nodeNameTran + '.color1')
    CleanConnectionOnNode(nodeNameTran, 'color2', True) 
    cmds.connectAttr(fj + '.translate', nodeNameTran + '.color2')
    CleanConnectionOnNode(nodeNameTran, 'output', False)
    cmds.connectAttr(nodeNameTran + '.output', rj + '.translate')
    CleanConnectionOnNode(nodeNameTran, 'blender', True)
    cmds.connectAttr(switchCtrl+'.'+switchAttr, nodeNameTran + '.blender')
 
    
    
    print("##[Link FK IK switch fnished!!]")
    
    return 1
    
    
def ArmIKFKBlendSetup(isRight):
    prefix = ''
    if isRight is True:
        prefix = 'r_'
        print('Current Set up right arm ik fk blend')
        #ArmInitJointNames(isRight)
        controlName = 'r_armSwitchCtrl'
        for jn in armResultJNT: 
            #print(jn) 
            if prefix in jn:
                CreateFKIKBlendForJoint(jn, controlName)
        
        
        
        
    return 1
    

def ConnectArmToTorso(isRight):
    print('##[Connect] Arm to torso')
    
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_' 
    
    # pivot for all arm grps 
    armpivot = armResultJNT['']
    
    
    print('##[Finished] Arm successfully connected to torso')
    return 1
    

###################
# main entry for ui 
###################

print(cmds.window("mainWindow", exists=True))

if (cmds.window("mainWindow", exists=True)):
		cmds.deleteUI("mainWindow")


mainWindow = cmds.window("mainWindow", title="Auto-Rig Setup", widthHeight=(800, 300) )

# As we add contents to the window, align them vertically
colMain = cmds.columnLayout( adjustableColumn=True )

cmds.rowLayout(numberOfColumns=5)
cmds.button( label='Set Up Right Arm FK, IK blend', command='ArmIKFKBlendSetup(True)')
cmds.button( label='Configure Right Arm Result JNT', command='ConfigResultArm(True)')
cmds.button( label='Configure Right Arm FK JNT', command='ConfigureFKArm(True)')
cmds.button( label='Configure Right Arm IK JNT', command='ConfigureIKArm(True)')
cmds.button( label='Connect Right Arm To Torso', command='ConnectArmToTorso(True)')
# A button that does nothing

cmds.setParent(colMain)

cmds.rowLayout(numberOfColumns=2)
cmds.button( label='Left Arm match to IK', command='lArmMatchFK2IK()')
cmds.button( label='Left Arm match to FK', command='lArmMatchIK2FK()')
#cmds.rowLayout(numberOfColumns=2)
# Close button with a command to delete the UI
#cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
# Set its parent to the Maya window (denoted by '..')
cmds.setParent( '..' )
# Show the window that we created (window)
cmds.showWindow( mainWindow )


ArmInitJointNames(True)

#CreateContorlCurvesAndParentTo("test", "test", (0,0,1))




