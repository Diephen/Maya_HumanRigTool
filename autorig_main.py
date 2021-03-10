import maya.cmds as cmds 
import math 
import sys
sys.setrecursionlimit(15000)


## Util functions


def getWSRotate(obj):
    rotate = cmds.xform(obj, q = True, ws = True, ro = True)
    return rotate
    
def getWSTranslate(obj):
    translate = cmds.xform(obj, q = True, ws = True, t = True)
    return translate


def getVectorMinus(va, vb):
    return (va[0] - vb[0], va[1] - vb[1], va[2] - vb[2])

def getVectorAdd(va, vb):
    return (va[0] + vb[0], va[1] + vb[1], va[2] + vb[2])
    
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
    if isinput:
        # check if anything is connected to the attr
        conn = cmds.listConnections(nodename+'.'+attrname, s=True, p = True, d = False)
        print('# check if anything is connected to the {0}: {1}' .format(nodename+'.'+attrname, conn))
        if conn is None or len(conn) == 0:
            print('not connected')
            return 0 
        else:
            cmds.disconnectAttr(conn[0], nodename+'.'+attrname)
            if 'unitConversion' in conn[0]:
                print('[Node deleted for cleanup]' + conn[0].split('.')[0])
                cmds.delete(conn[0].split('.')[0])
                
    else:
        # check if anything is taking the attr as the source
        
        conn = cmds.listConnections(nodename+'.'+attrname,s=False, p = True, d = True)
        print('# check if anything is taking {0} as the source: {1}' .format(nodename+'.'+attrname, conn))
        if conn == None or len(conn) == 0:
            print('not connected')
            return 0 
        else:
            cmds.disconnectAttr(nodename+'.'+attrname, conn[0])
            if 'unitConversion' in conn[0]:
                print('[Node deleted for cleanup]' + conn[0].split('.')[0])
                cmds.delete(conn[0].split('.')[0])
    
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




# clavicle
clavicleResultJNT = {}
clavicleCTRL = {}
    
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
centralResultJNT = {}

#leg chain 
legResultJNT = {}
legIKJNT = {}
legFKJNT = {}
legCTRL = {}
legGRP = {}
legStat = {}
legHDL = {}
legLOC = {}
legRigGroup = {'r_rigGRP':{}, 'l_rigGRP':{}}

# UI/animation control 
isMatchingRightKneeManual = True
isMatchingLeftKneeManual = True  
isTorsoStretching = True
isArmStretching = True
isLegStretching = True

def setArmStretching(isStretching):
    global isArmStretching
    isArmStretching = isStretching
    print('## Stretch&Squash is {} for both arms'.format(isArmStretching))
    safeSetAttr(armCTRL['r_Switch'], 'stretch_toggle', isStretching)
    safeSetAttr(armCTRL['l_Switch'], 'stretch_toggle', isStretching)

def setLegStretching(isStretching):
    global isLegStretching
    isLegStretching = isStretching
    print('## Stretch&Squash is {} for both legs'.format(isLegStretching))
    safeSetAttr(legCTRL['r_Switch'], 'stretch_toggle', isStretching)
    safeSetAttr(legCTRL['l_Switch'], 'stretch_toggle', isStretching)

def setTorsoStretching(isStretching):
    global isTorsoStretching
    isTorsoStretching = isStretching
    print('## Stretch&Squash is {} for torso'.format(isTorsoStretching))
    safeSetAttr(centralCTRL['shoulderCtrl'], 'stretch_toggle', isStretching)

def safeSetAttr(obj, attr, val):
    try:
        cmds.setAttr(obj+'.'+attr, val)
    except Error as e:
        print('[ERROR] Can not set attribute {0}, because of error: {1}'.format(obj+'.'+attr, e))
    


def setElbowForearmMatching(isRight, isFK):
    if isRight:
        global isMatchingRightFKForearm
        isMatchingRightFKForearm = isFK
        print('## Global Change: Matching Right arm to FK forearm is : {}'.format(isMatchingRightFKForearm))
    else:
        global isMatchingLeftFKForearm
        isMatchingLeftFKForearm = isFK
        print('## Global Change: Matching Left arm to FK forearm is : {}'.format(isMatchingLeftFKForearm))

isMatchingLeftFKForearm = False
isMatchingRightFKForearm = False   

def setKneeManualMatching(isRight, isManual):
    if isRight:
        global isMatchingRightKneeManual
        isMatchingRightKneeManual = isManual
        print('## Global Change: Matching Right leg to Manual Knee is : {}'.format(isMatchingRightKneeManual))
    else:
        global isMatchingLeftKneeManual
        isMatchingLeftKneeManual = isManual
        print('## Global Change: Matching Left leg to Manual Knee is : {}'.format(isMatchingLeftKneeManual))

def selectAllCtrl():
    cmds.select(gAllCtrls, hierarchy = False)

    return 0

# all ctrollers 
gAllCtrls = []
# Add contorller to the global ctrl array 
def registerNewController(ctrlName):
    exists, ctrl = CheckObjExists(ctrlName)
    if not exists:
        print ('## [WARNINH] Controller {} doesn\'t exist in the current scene, skip...'.format(ctrlName))
    else:
        if not ctrl in gAllCtrls:
            print ('## [Controller Regist] Adding Controller {}'.format(ctrlName))
            gAllCtrls.append(ctrl)

    return 0


def registerControllerBasedOnNameConvenstion():
    # arm ctrls 
    for v in armCTRL.values():
        registerNewController(v)
    # leg ctrls
    for v in legCTRL.values():
        registerNewController(v)
    # clavicle ctrls
    for v in clavicleCTRL.values():
        registerNewController(v)
    # center ctrls 
    for v in centralCTRL.values():
        registerNewController(v)
    
    print('Total Controller in Scene: {}'.format(len(gAllCtrls)))
    return 0



def keyAllCtrl():
    print(gAllCtrls)
    for ctrl in gAllCtrls:
        allattr = cmds.listAttr(ctrl, keyable = True)
        for at in allattr:
            if at != 'visibility':
                try:
                    cmds.setKeyframe(ctrl, at = at, time = cmds.currentTime(q = True))
                except error as e:
                    print('Failed to set key on {}, skipped'.format(ctrl+'.'+at))
                    continue
    return 0


def selectAllGEO():
    return 0

def selectAllResultJNT():
    return 0

def selectForExport():
    selectAllGEO()
    selectAllResultJNT()

def generateGameRig():
    # dup result joint and connect it as a entire rig 

    # add root joint

    # generate 1-1 map for the result joints in profuction rig and game rig 

    return 0

def copySkinWeight():
    # copy skin weight from production rig to game rig 


    return 0




#Initialize joint names
#TODO: add verification steps 
def InitJointNames():
    #traverse ans assign joint names to vars 
    #TODO add name checks
    print("Init names")
    
    ## Central ##
    global centralResultJNT 
    centralResultJNT = {'root': 'root_JNT', 'pelvis': 'pelvis_JNT', 'spine01':'spine_01_JNT', 'spine02':'spine_02_JNT', 'spine03':'spine_03_JNT', 'spine04':'spine_04_JNT',
                        'neck01':'neck_01_JNT', 'neck02': 'neck_02_JNT', 'neck03': 'neck_03_JNT', 'head':'head_JNT'}
    global centralCTRL
    centralCTRL = {'rootCtrl':'Root_transform_CTRL', 'shoulderCtrl': 'shoulder_IK_CTRL', 'pelvisCtrl':'pelvis_IK_CTRL', 'spine01Ctrl':'spine_01_FK_CTRL', 'spine02Ctrl':'spine_02_FK_CTRL', 'neckCtrl':'neck_FK_CTRL', 'headCtrl':'head_CTRL'}
    
    global partSpaceGRP
    partSpaceGRP = {'root':'Root_transform_CTRL', 'body':'torso_rig_GRP', 'shoulder':'shoulder_bind_JNT', 'pelvis':'pelvis_bind_JNT'}
    
    ## Clavicle ##
    global clavicleResultJNT
    clavicleResultJNT = {'r_clavicle': 'clavicle_r_JNT', 'r_clavicleEnd':'clavicle_r_end_JNT',
                         'l_clavicle': 'clavicle_l_JNT', 'l_clavicleEnd':'clavicle_l_end_JNT'}

    global clavicleCTRL 
    clavicleCTRL = {'r_clavicle':'clavcle_r_CTRL', 'l_clavicle':'clavcle_l_CTRL'}

    ## Finger 
    global fingerCTRL
    fingerCTRL = {}
    
    global fingerResultJNT
    fingerResultJNT = {'r_finger01':'finger_01_r_JNT', 'r_finger02':'finger_02_r_JNT','r_finger03':'finger_03_r_JNT','r_finger04':'finger_04_r_JNT',
                       'l_finger01':'finger_01_l_JNT', 'l_finger02':'finger_02_l_JNT','l_finger03':'finger_03_l_JNT','l_finger04':'finger_04_l_JNT',
                       'r_thumb01':'thumb_01_r_JNT', 'r_thumb02':'thumb_02_r_JNT','r_thumb03':'thumb_03_r_JNT','r_thumbOrient':'thumb_orient_r_JNT',
                       'l_thumb01':'thumb_01_l_JNT', 'l_thumb02':'thumb_02_l_JNT','l_thumb03':'thumb_03_l_JNT','l_thumbOrient':'thumb_orient_l_JNT'}


    ## Arms ## 
    # Note: for result, ik and fk jnt, the entry for dictionary is the same for later fuctionality (blend all three types of jnts)
    global armHDL
    armHDL = {'r_armHDL' : 'arm_r_IK_HDL', 'r_handHDL':'hand_r_IK_HDL',
              'l_armHDL' : 'arm_l_IK_HDL', 'l_handHDL':'hand_l_IK_HDL'}
    
    global armGRP
    armGRP = {'r_armRigGRP':'arm_r_rig_GRP','r_HDLConstGRP':'arm_r_HDLConst_GRP', 'r_IKConstGRP':'arm_r_IKConst_GRP', 'r_FKConstGRP':'arm_r_FKConst_GRP', 'r_ResultConstGRP':'arm_r_resultConst_GRP', 'r_GimbleConstGRP':'arm_r_gimbleConst_GRP',
              'l_armRigGRP':'arm_l_rig_GRP','l_HDLConstGRP':'arm_l_HDLConst_GRP', 'l_IKConstGRP':'arm_l_IKConst_GRP', 'l_FKConstGRP':'arm_l_FKConst_GRP', 'l_ResultConstGRP':'arm_l_resultConst_GRP', 'l_GimbleConstGRP':'arm_l_gimbleConst_GRP'}
    global armStat
    armStat = {'r_UpperarmIKLength': 38.975, 'r_LowerarmIKLength':74.429, 'r_lowerarmTranslateX': 38.975, 'r_wristTranslateX': 74.429, 'r_IKtotalLength': 113.413, 'r_armXDir':1,
               'l_UpperarmIKLength': 38.975, 'l_LowerarmIKLength':74.429, 'l_lowerarmTranslateX': -38.975, 'l_wristTranslateX': -74.429, 'l_IKtotalLength': 113.403, 'l_armXDir':-1}
    global armCTRL
    armCTRL = { 'r_Switch':'RIGHT_arm_IKFK_SWITCH', 'r_gimbleCtrl' : 'arm_r_GIMBLE_CTRL',
                'r_UpperarmCtrl':'upperarm_r_FK_JNT', 'r_LowerarmCtrl': 'lowerarm_r_FK_JNT', 'r_wristCtrl': 'wrist_r_FK_JNT',
                'r_armIKCtrl':'r_arm_IK_CTRL', 'r_elbowIKLOC': 'r_elbow_LOC','r_elbowIKCtrl': 'r_elbow_PV_CTRL', 'r_elbowFK_Lowerarm':'elbow_lowerarm_r_FK_JNT','r_elbowFK_wrist':'elbow_wrist_r_FK_JNT', 'r_elbowFK_hand':'elbow_hand_r_FK_JNT',
                'l_Switch':'LEFT_arm_IKFK_SWITCH', 'l_gimbleCtrl' : 'arm_l_GIMBLE_CTRL',
                'l_UpperarmCtrl':'upperarm_l_FK_JNT', 'l_LowerarmCtrl': 'lowerarm_l_FK_JNT', 'l_wristCtrl': 'wrist_l_FK_JNT',
                'l_armIKCtrl':'l_arm_IK_CTRL', 'l_elbowIKLOC': 'l_elbow_LOC','l_elbowIKCtrl': 'l_elbow_PV_CTRL', 'l_elbowFK_Lowerarm':'elbow_lowerarm_l_FK_JNT','l_elbowFK_wrist':'elbow_wrist_l_FK_JNT', 'l_elbowFK_hand':'elbow_hand_l_FK_JNT'}
  
    global armResultJNT 
    armResultJNT = {'r_Upperarm': 'upperarm_r_JNT', 'r_Lowerarm': 'lowerarm_r_JNT', 'r_Wrist': 'wrist_r_JNT', 'r_Hand' : 'hand_r_JNT',
                    'l_Upperarm': 'upperarm_l_JNT', 'l_Lowerarm': 'lowerarm_l_JNT', 'l_Wrist': 'wrist_l_JNT', 'l_Hand' : 'hand_l_JNT'}
    global armIKJNT 
    armIKJNT = {'r_Upperarm': 'upperarm_r_IK_JNT', 'r_Lowerarm': 'lowerarm_r_IK_JNT', 'r_Wrist': 'wrist_r_IK_JNT', 'r_Hand' : 'hand_r_IK_JNT',
                'l_Upperarm': 'upperarm_l_IK_JNT', 'l_Lowerarm': 'lowerarm_l_IK_JNT', 'l_Wrist': 'wrist_l_IK_JNT', 'l_Hand' : 'hand_l_IK_JNT'}
    global armFKJNT 
    armFKJNT = {'r_Upperarm': 'upperarm_r_FK_JNT', 'r_Lowerarm': 'lowerarm_r_FK_JNT', 'r_Wrist': 'wrist_r_FK_JNT', 'r_Hand' : 'hand_r_FK_JNT',
                'l_Upperarm': 'upperarm_l_FK_JNT', 'l_Lowerarm': 'lowerarm_l_FK_JNT', 'l_Wrist': 'wrist_l_FK_JNT', 'l_Hand' : 'hand_l_FK_JNT'}
    
    
    #init global leg name vars 
    global legResultJNT
    legResultJNT = {'r_Thigh': 'thigh_r_JNT', 'r_Calf': 'calf_r_JNT', 'r_Foot': 'foot_r_JNT', 'r_Ball' : 'ball_r_JNT', 'r_Toe': 'toe_r_JNT',
                    'l_Thigh': 'thigh_l_JNT', 'l_Calf': 'calf_l_JNT', 'l_Foot': 'foot_l_JNT', 'l_Ball' : 'ball_l_JNT', 'l_Toe': 'toe_l_JNT'}
    
    global legFKJNT
    legFKJNT = {'r_Thigh': 'thigh_r_FK_JNT', 'r_Calf': 'calf_r_FK_JNT', 'r_Foot': 'foot_r_FK_JNT', 'r_Ball' : 'ball_r_FK_JNT', 'r_Toe': 'toe_r_FK_JNT',
                'l_Thigh': 'thigh_l_FK_JNT', 'l_Calf': 'calf_l_FK_JNT', 'l_Foot': 'foot_l_FK_JNT', 'l_Ball' : 'ball_l_FK_JNT', 'l_Toe': 'toe_l_FK_JNT'}

    global legIKJNT
    legIKJNT = {'r_Thigh': 'thigh_r_IK_JNT', 'r_Calf': 'calf_r_IK_JNT', 'r_Foot': 'foot_r_IK_JNT', 'r_Ball' : 'ball_r_IK_JNT', 'r_Toe': 'toe_r_IK_JNT',
                'r_ThighAuto': 'thigh_r_IK_Auto_JNT', 'r_CalfAuto': 'calf_r_IK_Auto_JNT', 'r_FootAuto': 'foot_r_IK_Auto_JNT','r_BallAuto' : 'ball_r_IK_Auto_JNT', 'r_ToeAuto': 'toe_r_IK_Auto_JNT',
                'r_ThighManual': 'thigh_r_IK_Manual_JNT', 'r_CalfManual': 'calf_r_IK_Manual_JNT', 'r_FootManual': 'foot_r_IK_Manual_JNT','r_BallManual' : 'ball_r_IK_Manual_JNT', 'r_ToeManual': 'toe_r_IK_Manual_JNT',
                'l_Thigh': 'thigh_l_IK_JNT', 'l_Calf': 'calf_l_IK_JNT', 'l_Foot': 'foot_l_IK_JNT', 'l_Ball' : 'ball_l_IK_JNT', 'l_Toe': 'toe_l_IK_JNT',
                'l_ThighAuto': 'thigh_l_IK_Auto_JNT', 'l_CalfAuto': 'calf_l_IK_Auto_JNT', 'l_FootAuto': 'foot_l_IK_Auto_JNT', 'l_BallAuto' : 'ball_l_IK_Auto_JNT', 'l_ToeAuto': 'toe_l_IK_Auto_JNT',
                'l_ThighManual': 'thigh_l_IK_Manual_JNT', 'l_CalfManual': 'calf_l_IK_Manual_JNT', 'l_FootManual': 'foot_l_IK_Manual_JNT', 'l_BallManual' : 'ball_l_IK_Manual_JNT', 'l_ToeManual': 'toe_l_IK_Manual_JNT'}

    global legHDL
    legHDL = {'r_Ball':'ball_r_IK_HDL', 'r_Toe':'toe_r_IK_HDL', 'r_KneeAuto':'leg_r_KneeAutoIK_HDL', 'r_KneeManual':'leg_r_KneeManualIK_HDL',
              'l_Ball':'ball_l_IK_HDL', 'l_Toe':'toe_l_IK_HDL', 'l_KneeAuto':'leg_l_KneeAutoIK_HDL', 'l_KneeManual':'leg_l_KneeManualIK_HDL'}
    
    global legCTRL
    legCTRL = {'r_Switch':'RIGHT_leg_IKFK_SWITCH', 'r_FootIK': 'foot_r_IK_CTRL', 'r_KneeIKManual':'leg_r_KneeIKManual_CTRL','r_KneeIKAuto':'leg_r_KneeIKAuto_CTRL','r_ThighFK' : 'thigh_r_FK_JNT', 'r_CalfFK' : 'calf_r_FK_JNT', 'r_FootFK' : 'foot_r_FK_JNT', 'r_BallFK' : 'ball_r_FK_JNT', 
               'l_Switch':'LEFT_leg_IKFK_SWITCH','l_FootIK': 'foot_l_IK_CTRL', 'l_KneeIKManual':'leg_l_KneeIKManual_CTRL','l_KneeIKAuto':'leg_l_KneeIKAuto_CTRL','l_ThighFK' : 'thigh_l_FK_JNT', 'l_CalfFK' : 'calf_l_FK_JNT', 'l_FootFK' : 'foot_l_FK_JNT', 'l_BallFK' : 'ball_l_FK_JNT'}
    
    global legGRP
    legGRP = {'r_RigGRP':'leg_r_rig_GRP','r_HDLConstGRP':'leg_r_HDLConst_GRP', 'r_IKConstGRP':'leg_r_IKConst_GRP', 'r_FKConstGRP':'leg_r_FKConst_GRP', 'r_ResultConstGRP':'leg_r_resultConst_GRP', 'r_AutoKneeGRP': 'leg_r_IKAutoKnee_GRP', 'r_ManualKneeGRP': 'leg_r_IKManualKnee_GRP', 'r_footHDL' : 'foot_r_HDLGRP', 'r_FootLocGRP':'foot_r_LOC_GRP',
              'l_RigGRP':'leg_l_rig_GRP','l_HDLConstGRP':'leg_l_HDLConst_GRP', 'l_IKConstGRP':'leg_l_IKConst_GRP', 'l_FKConstGRP':'leg_l_FKConst_GRP', 'l_ResultConstGRP':'leg_l_resultConst_GRP', 'l_AutoKneeGRP': 'leg_l_IKAutoKnee_GRP', 'l_ManualKneeGRP': 'leg_l_IKManualKnee_GRP', 'l_footHDL' : 'foot_l_HDLGRP', 'l_FootLocGRP':'foot_l_LOC_GRP'}

    global legStat
    legStat = {'r_thighIKLength': 78.523, 'r_calfIKLength': 131.489, 'r_calfTranslateX': -64.25, 'r_footTranslateX': -120.068, 'r_IKtotalLength': 183.319, 'r_defaultKneeTwist' : -90, 'r_legXDir': -1,
               'l_thighIKLength': 78.523, 'l_calfIKLength': 131.489, 'l_calfTranslateX': 64.25, 'l_footTranslateX': 120.068, 'l_IKtotalLength': 183.319, 'l_defaultKneeTwist': -90, 'l_legXDir': 1}

    global legLOC
    legLOC = {}
    # end of leg name vars 

    # TODO: read the Stat vars from data file as these vars will be initated during setup and stay constant 


    return 1
    
## add objs to rig group 
   

    
# attach proxy mesh 
def CreateProxyMeshGRP(jntName, jnt):
    grpName = jntName+'_ProxyGEO_GRP'
    grpSearch = cmds.ls(grpName)
    
    # TODO: need to align the group rot x axis with the coresponding joint local x
    if grpSearch == None or len(grpSearch) is 0: 
        print("Create proxy group")
        grp = cmds.group(n = grpName, p = jnt, em = True)
        print(grp)
        #cmds.manipPivot(grp, p = getWSTranslate(armResultJNT[jntName]))
    else:
        print("GRP already exists")
        #link the result jnt translate X val with the proxy geoGRP
        
        
    return 0
    
# setting up result arm for rigging 
# create empty grp node for each result joint as the slot for the proxy mesh         
def ConfigureResultJoint(isRight, partName):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else: 
        prefix = 'l_'

    ResultJNT = {}
    GEP = {}
    if partName == 'arm':
        ResultJNT = armResultJNT
        GRP = armGRP
    elif partName == 'leg':
        ResultJNT = legResultJNT
        GRP = legGRP
    else:
        print('##[ERROR] Invalid part name {}, exit setup !! '.format(partName))
        return 0

    print('Create empty grps for proxy mesh')
    for jn in ResultJNT: 
        if prefix in jn:
            CreateProxyMeshGRP(jn, ResultJNT[jn])
                
    # link procy grp scaleX with jnt translate X 
   
    if partName == 'arm' : 
         # Upperarm stretch
        proxyGRP = prefix+'Upperarm_ProxyGEO_GRP'
        nodename = prefix + 'Upperarm_Stretch_DefaultLengthDiv'
        exists, defaultLengthDiv = CheckObjExists(nodename)
        if not exists:
            defaultLengthDiv = cmds.createNode('multiplyDivide', n = nodename)
            
        cmds.setAttr(defaultLengthDiv+'.operation', 2)
        CleanConnectionOnNode(defaultLengthDiv, 'input1X', True)
        cmds.connectAttr(armResultJNT[prefix+'Lowerarm']+ '.translateX', defaultLengthDiv + '.input1X', )
        CleanConnectionOnNode(defaultLengthDiv, 'input2X', True)
        cmds.setAttr(defaultLengthDiv + '.input2X', armStat[prefix+'lowerarmTranslateX'])
        CleanConnectionOnNode(defaultLengthDiv, 'outputX', False)
        CleanConnectionOnNode(proxyGRP, 'scaleX', True)
        cmds.connectAttr(defaultLengthDiv+'.outputX', proxyGRP + '.scaleX')
        
        
        # Lowerarm stretch
        proxyGRP = prefix+'Lowerarm_ProxyGEO_GRP'
        nodename = prefix + 'Lowerarm_Stretch_DefaultLengthDiv'
        exists, defaultLengthDiv = CheckObjExists(nodename)
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

        grpName = GRP[prefix+'ResultConstGRP']
        grpChild = ResultJNT[prefix+'Upperarm']
        CreateGroupWithChild(grpName, grpChild)

    else:
        # thigh stretch 
        proxyGRP = prefix+'Thigh_ProxyGEO_GRP'
        nodename = prefix + 'Thigh_Stretch_DefaultLengthDiv'
        exists, defaultLengthDiv = CheckObjExists(nodename)
        if not exists:
            defaultLengthDiv = cmds.createNode('multiplyDivide', n = nodename)
            
        cmds.setAttr(defaultLengthDiv+'.operation', 2)
        CleanConnectionOnNode(defaultLengthDiv, 'input1X', True)
        cmds.connectAttr(legResultJNT[prefix+'Calf']+ '.translateX', defaultLengthDiv + '.input1X', )
        CleanConnectionOnNode(defaultLengthDiv, 'input2X', True)
        cmds.setAttr(defaultLengthDiv + '.input2X', legStat[prefix+'calfTranslateX'])
        CleanConnectionOnNode(defaultLengthDiv, 'outputX', False)
        CleanConnectionOnNode(proxyGRP, 'scaleX', True)
        cmds.connectAttr(defaultLengthDiv+'.outputX', proxyGRP + '.scaleX')

        # calf stretch 
        proxyGRP = prefix+'Calf_ProxyGEO_GRP'
        nodename = prefix + 'Calf_Stretch_DefaultLengthDiv'
        exists, defaultLengthDiv = CheckObjExists(nodename)
        if not exists:
            defaultLengthDiv = cmds.createNode('multiplyDivide', n = nodename)
            
        cmds.setAttr(defaultLengthDiv+'.operation', 2)
        CleanConnectionOnNode(defaultLengthDiv, 'input1X', True)
        cmds.connectAttr(legResultJNT[prefix+'Foot']+ '.translateX', defaultLengthDiv + '.input1X', )
        CleanConnectionOnNode(defaultLengthDiv, 'input2X', True)
        cmds.setAttr(defaultLengthDiv + '.input2X', legStat[prefix+'footTranslateX'])
        CleanConnectionOnNode(defaultLengthDiv, 'outputX', False)
        CleanConnectionOnNode(proxyGRP, 'scaleX', True)
        cmds.connectAttr(defaultLengthDiv+'.outputX', proxyGRP + '.scaleX')
    
        # group the result jnt chain
        grpName = GRP[prefix+'ResultConstGRP']
        grpChild = ResultJNT[prefix+'Thigh']
        CreateGroupWithChild(grpName, grpChild)
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
        
# create a group and set the pivot of new grp to the child world position
def CreateGroupWithChild(gname, gchild):
    grpname = gname
    grpchild = gchild
    grppivot = getWSTranslate(grpchild)
    
    if math.pow(grppivot[0],2)+math.pow(grppivot[1],2)+math.pow(grppivot[2],2) == 0 :
        grppivot = getWRPivot(grpchild)
        
    print('## child Pivot is: {0}'.format(grppivot))
    exists, grp = CheckObjExists(grpname)
    grpparent = cmds.listRelatives(grpchild, p = True)
    if not grpparent == None:
        grpparent = grpparent[0]
        print('#Current Parent GRP:' + grpparent)
        
    if not exists:
        # create empty grp 
        if not grpparent == None: 
            grp = cmds.group(n = grpname, p = grpparent, em = True)
        else:
            grp = cmds.group(n = grpname, w = True, em = True)
    # set the grp pivot to the child pivot 
    print("## Change pivot of :" + grp)
    
    cmds.xform(grp, pivots = grppivot)
    if not grpparent == grpname:   
        # parent child to the grp
        print('## reparent :' + grpchild)
        cmds.parent(grpchild, grp)
        
    return 0
    
def AddToGroup(gname, gchild):
    curparent = cmds.listRelatives(gchild, parent = True)
    if curparent == None or curparent[0] != gname:
        cmds.parent(gchild, gname)
    else:
        print('[Group] {0} is already under group {1}'.format(gchild, gname))

def RemoveFromGroup(gname, gchild):
    curparent = cmds.listRelatives(gchild, parent = True)
    if curparent == None or curparent[0] != gname:
        print('[Group] {0} is not under group {1}'.format(gchild, gname))
    else:
        cmds.ungroup(gchild, w = True)

def DuplicateJointChain(fistJntName, firstJnt, numOfChildren):
    cnodes = []
    exists, firstjnt = CheckObjExists(fistJntName)
    isDuplicate = False
    if exists:
        # double check all children 
        cnodes = cmds.listRelatives(firstjnt, allDescendents = True)
        print(cnodes)
        if cnodes == None or len(cnodes) != numOfChildren:
            isDuplicate = True 
            cmds.delete(firstjnt)
    else:
        isDuplicate = True
    
    if isDuplicate:
        cnodes = cmds.duplicate(firstJnt, rc = True, ic = False)
    else:
        cnodes.append(firstjnt)

    return cnodes

## Configure FK arm 
def ConfigureFKArm(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
        controlPrefix = 'RIGHT_'
    else: 
        prefix = 'l_'
        controlPrefix = 'LEFT_'
    
    print('Create Ctrls for FK joints')
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
    
    # Create arm_Gimble_GRP under the resultConst_GRP  
    # parent Upperarm fk chain under gimble_ctrl 
    # create bimble choice 
    print('## Create Gimble correction ctrl')
    gimblename = armCTRL[prefix+'gimbleCtrl']
    exists, gimbleCtrl = CheckObjExists(gimblename)
    if not exists:
        print('No ctrl exists, prompt the creation warning')
        return 0
   
    pivotPos = getWSTranslate(armResultJNT[prefix+'Upperarm'])    
    if cmds.listRelatives(armFKJNT[prefix+'Upperarm'], p = True) == None or not cmds.listRelatives(armFKJNT[prefix+'Upperarm'], p = True)[0] == armCTRL[prefix+'gimbleCtrl']:
        cmds.parent(armFKJNT[prefix+'Upperarm'], armCTRL[prefix+'gimbleCtrl'])
 
    #Create arm_FKconst_GRP
    print('##create fk const grp')
    grpname = armGRP[prefix+'FKConstGRP']
    grpchild = armCTRL[prefix+'gimbleCtrl']
    CreateGroupWithChild(grpname, grpchild)
    
    #Create gimbleConst_GRP under ResultConst_GRP
    grpname = armGRP[prefix+'GimbleConstGRP']
    grpchild = armResultJNT[prefix+'Upperarm']
    CreateGroupWithChild(grpname, grpchild)
    
    # constraint the gimble grp to the gimble control when in FK mode
    # if fkik blend = 0, blender color 2 = gimble constraint 
    gimbleGRP = armGRP[prefix+'GimbleConstGRP']
    targets = []
    targets.append(armCTRL[prefix+'gimbleCtrl'])
    exists, constraint = CheckObjExists(prefix+'armGimbleOrientConstraint')
    if not exists:
        constraint = cmds.orientConstraint(targets, gimbleGRP, name = prefix+'armGimbleOrientConstraint')[0]
    print (constraint)
    
    # create blend choice 
    bname = prefix + 'arm_GimbleChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
        
    CleanConnectionOnNode(bnode, 'color1', True)    
    cmds.setAttr(bnode + '.color1', 0,0,0, type = 'double3')
    CleanConnectionOnNode(bnode, 'color2', True) 
    cmds.connectAttr(constraint + '.constraintRotate', bnode + '.color2')
    CleanConnectionOnNode(bnode, 'output', False)
    CleanConnectionOnNode(gimbleGRP ,'rotate',True)
    CleanConnectionOnNode(gimbleGRP ,'rotateX',True)
    CleanConnectionOnNode(gimbleGRP ,'rotateY',True)
    CleanConnectionOnNode(gimbleGRP ,'rotateZ',True)
    cmds.connectAttr(bnode + '.output', gimbleGRP + '.rotate')
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(armCTRL[prefix+'Switch']+'.FKIK_blend', bnode + '.blender')
    
  
    obj = armCTRL[prefix+'gimbleCtrl']
    expname = prefix+'arm_GimbleCtrlVisibility_expression'
    cmds.delete(obj, at = 'visibility', e = True)
    expstring = "if({cPrefix}arm_IKFK_SWITCH.FKIK_blend == 1){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(cPrefix = controlPrefix, jname = obj)
    print(expstring)
    cmds.expression(o = constraint, s = expstring, ae = True, name = expname)
    
    print('##[Finished] Gimble set up success')
        
    
    
    print('## setting up FK ARM stretch & squash')
    #adding stretch&squash function to FK arm joint
    switchCtrl = armCTRL[prefix+'Switch']
    attrname = 'stretch_toggle'
    exists = CheckAttributeExists(switchCtrl, attrname)
    if not exists:
        cmds.addAttr(switchCtrl, longName = attrname, niceName = 'Stretch Toggle', at = 'bool', dv = 1, k = True)
    

    nname = armCTRL[prefix+'UpperarmCtrl']
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
        cmds.setDrivenKeyframe(armFKJNT[prefix+'Lowerarm'], attribute='translateX', currentDriver = nname+'.length', driverValue = 0, value = 0)
        cmds.setDrivenKeyframe(armFKJNT[prefix+'Lowerarm'], attribute='translateX', currentDriver = nname+'.length', driverValue = 1, value = translateX)
    cmds.setAttr(nname+'.'+attr, 1)
        # update the animation curve 
    cmds.keyTangent(armFKJNT[prefix+'Lowerarm'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(armFKJNT[prefix+'Lowerarm']+'.translateX', poi = 'linear')

    # add stretch toggle 
    animNode = 'lowerarm_' + prefix + 'FK_JNT_translateX'
    bname = prefix+'arm_UpperarmStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(armFKJNT[prefix+'Upperarm']+'.length', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', 1)
    CleanConnectionOnNode(animNode, 'input', True)
    CleanConnectionOnNode(bnode, 'outputR', False)
    cmds.connectAttr(bnode+'.outputR', animNode+'.input')

    nname = armCTRL[prefix+'LowerarmCtrl']
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
    cmds.keyTangent(armFKJNT[prefix+'Wrist'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(armFKJNT[prefix+'Wrist']+'.translateX', poi = 'linear')

    bname = prefix+'arm_LowerarmStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    animNode = 'wrist_' + prefix + 'FK_JNT_translateX'
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(armFKJNT[prefix+'Lowerarm']+'.length', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', 1)
    CleanConnectionOnNode(animNode, 'input', True)
    CleanConnectionOnNode(bnode, 'outputR', False)
    cmds.connectAttr(bnode+'.outputR', animNode+'.input')

    ## setup snap jnts 
    jntlist = ['Upperarm', 'Lowerarm', 'Wrist']
    for jn in jntlist:
        parentjnt = armResultJNT[prefix+jn]
        copyjnt = armFKJNT[prefix+jn]
        newname = armFKJNT[prefix+jn]+'SnapTo'
        exists, snapjnt = CheckObjExists(newname)
        if exists:
            cmds.delete(snapjnt)
        snapjnt = cmds.duplicate(copyjnt, name = newname, parentOnly = True)
        existparent = cmds.listRelatives(snapjnt, parent = True)
        if existparent is None or not (existparent[0] is parentjnt):
            cmds.parent(snapjnt, parentjnt)
        existshape = cmds.listRelatives(snapjnt, shapes = True)
        if not (existshape is None) and len(existshape) > 0:
            cmds.delete(snapjnt, shapes = True)
        cmds.setAttr(snapjnt[0]+'.visibility', 0)

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
    lengthNodes = []
    ikname = armCTRL[prefix+'armIKCtrl']
    exists, IKCtrl = CheckObjExists(ikname)
    if not exists:
        print('[WARNING] IK arm controller: {}  non exists, please add it to the scene !!'.format(ikname))
        return 0
    IKCtrl = armCTRL[prefix+'armIKCtrl']

    ctrlname = armCTRL[prefix+'elbowIKCtrl']
    exists, elbowCtrl = CheckObjExists(ctrlname)
    if not exists:
        print('[WARNING] IK elbow controller: {}  non exists, please add it to the scene !!'.format(ctrlname))
        return 0
    elbowCtrl = armCTRL[prefix+'elbowIKCtrl']

    # move IK ctrl to match wrist joint position & rotation 
    #cmds.xform(IKCtrl, t = getWSTranslate(armIKJNT[prefix+'Wrist']), ws = True)

    print ('## Setup leg IK solvers, footIK, ballIK, toeIK')
    # TODO: add a warning msg to setup a prefered angle
    print ('Please make sure the elbow is bent !! Continue / Abort')

    startjnt = armIKJNT[prefix+'Upperarm']
    endjnt = armIKJNT[prefix+'Wrist']
    # footIK Manual Knee set up, with pull vector knee 
    hdlname = armHDL[prefix+'armHDL']
    exists, armIKHDL = CheckObjExists(hdlname)
    if not exists:
        armIKHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikRPsolver', sticky = 'sticky')[0]

    startjnt = armIKJNT[prefix+'Wrist']
    endjnt = armIKJNT[prefix+'Hand']
    hdlname = armHDL[prefix+'handHDL']
    exists, handIKHDL = CheckObjExists(hdlname)
    if not exists:
        handIKHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikSCsolver', sticky = 'sticky')[0]

    
    #add elbow contorl 
    elbowCtrl = armCTRL[prefix+'elbowIKCtrl']
    elbowLoc = armCTRL[prefix+'elbowIKLOC']

    # create arm elbow loc
    locName = armCTRL[prefix+'elbowIKLOC']
    exists, elbowLoc = CheckObjExists(locName)
    offset = [0,0,-gSceneScale * 3]
    jointPos = getWSTranslate(armIKJNT[prefix+'Lowerarm'])
    position = getVectorAdd(jointPos, offset)
    if exists:
        print('Nee to delete {}'.format(elbowLoc))
        cmds.delete(elbowLoc)
    elbowLoc = cmds.spaceLocator(n = locName) [0]
    cmds.setAttr(elbowLoc+'.visibility', 0)
    print(position)
    cmds.xform (elbowCtrl, t = position, ws = True)
    cmds.xform (elbowLoc, t = position, ws = True)
    AddToGroup(elbowCtrl, elbowLoc) 
    
    
    # add pole vector constraint 
    pvname = 'arm_{prefix}_Elbow_PVConstraint'.format(prefix=prefix)
    exist, pvconstraint = CheckObjExists(pvname)
    if exists:
        cmds.delete(pvconstraint)
    cmds.poleVectorConstraint(elbowLoc, armIKHDL, name = pvname)

    # move elbowctrl and parent elbow loc under it 

     

    attr = 'elbow_snap'
    if not CheckAttributeExists(elbowCtrl, attr):
        cmds.addAttr(elbowCtrl, ln = attr, at = 'float', min = 0, max = 1, k = True, nn = 'Elbow Snap')
    attr = 'elbow_fkik_blend'
    if not CheckAttributeExists(elbowCtrl, attr):
        cmds.addAttr(elbowCtrl, ln = attr, at = 'float', min = 0, max = 1, k = True, nn = 'Elbow FK/IK Blend')
        
 
    
    #duplicate FK ctrl from Lowerarm to hand , rename with elnow prefix 
    #parent under the elbowCtrl, move to the same location 
    
    exists, elbowLowerarm = CheckObjExists(armCTRL[prefix+'elbowFK_'+'hand'])
    elbowChain = []
    if not exists:
        elbowLowerarm = cmds.duplicate(armFKJNT[prefix+'Lowerarm'], ic = False, rc = True)
        for e in elbowLowerarm:
            name = e.split(prefix + 'FK_JNT')
            newname = 'elbow_' + name[0] + prefix + 'FK_JNT'
            en = cmds.rename(e, newname)
            elbowChain.append(en)
    else:
        print("Elbow fk chain exists , skip creation ")
        elbowLowerarm = cmds.ls(armCTRL[prefix+'elbowFK_'+'Lowerarm'])
        elbowChain.append(elbowLowerarm)
    cmds.setAttr(armCTRL[prefix+'elbowFK_'+'wrist']+'.visibility', 1)
    
    cmds.xform(elbowChain[0], t = getWSTranslate(elbowCtrl), ws = True)
    
    # reparent the chain 
    print(elbowChain[0])
    AddToGroup(elbowCtrl, elbowChain[0])
    
    
    ##
    ## Elbow FKIK hybrid control solution  
    ##
    
    # set up parent constraint on arm_ctrl, elbowFK_wrist, and the arm_HDLConst_GRP 
    # TODO: need to make sure the ik ctrl, grp and wrist joint has the same local axis
    IKConstGRPName = armGRP[prefix+'HDLConstGRP']
    exists, IKConstGRP = CheckObjExists (IKConstGRPName)
    armIKHDL = armHDL[prefix+'armHDL']
    handIKHDL = armHDL[prefix+'handHDL']
    if not exists:
        cmds.group(name = IKConstGRPName, parent = armIKJNT[prefix+'Wrist'], em = True)
        cmds.parent(IKConstGRPName, w = True)

    AddToGroup(IKConstGRPName, armIKHDL)
    AddToGroup(IKConstGRPName, handIKHDL)

    
    targets = [armCTRL[prefix+'armIKCtrl'], armCTRL[prefix+'elbowFK_wrist']]
    print (targets)
    constraintName = prefix+'elbowFKIKChoice_parentConstraint'
    exists, constraint = CheckObjExists(constraintName)
    if exists:
        cmds.delete(constraint)
    constraint = cmds.parentConstraint(targets, IKConstGRP, name = constraintName, mo = False)[0]
    print (constraint)
    
    #return 0
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
    visContorl = armCTRL[prefix+'elbowFK_'+'Lowerarm']
    print(visContorl)
    cmds.delete(visContorl, at = 'visibility', e = True)
    expstring = "if({cprefix}arm_IKFK_SWITCH.FKIK_blend == 0 || {elbow}.elbow_fkik_blend >= 0.99){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(elbow = armCTRL[prefix+'elbowIKCtrl'], jname = visContorl, cprefix = contorlPrefix)
    print(expstring)
    cmds.expression(o = visContorl, s = expstring, ae = True) 
    
    
    ## 
    ## Create FKIK snap loators
    ## - copy paste to result grps 
    print("## set up IK snap contorls")
    parentjnt = armResultJNT[prefix+'Wrist']
    copyctrl = armCTRL[prefix+'armIKCtrl']
    newname = armCTRL[prefix+'armIKCtrl']+'SnapTo'
    exists, snapctrl = CheckObjExists(newname)
    if exists:
        cmds.delete(snapctrl)
    snapctrl = cmds.duplicate(copyctrl, name = newname, parentOnly = True)
    AddToGroup(parentjnt, snapctrl)
    cmds.setAttr(snapctrl[0]+'.visibility', 0)

    # add the default ctrl to the arm rig group
    grpname = armGRP[prefix+'armRigGRP']
    exists, rigGRP = CheckObjExists(grpname)
    if not exists:
        cmds.group(name = grpname, em = True, w = True)
    
    parentjnt = armGRP[prefix+'armRigGRP']
    copyctrl = armCTRL[prefix+'armIKCtrl']
    newname = armCTRL[prefix+'armIKCtrl']+'Default'
    exists, snapctrl = CheckObjExists(newname)
    if exists:
        cmds.delete(snapctrl)
    snapctrl = cmds.duplicate(copyctrl, name = newname, parentOnly = True)
    AddToGroup(parentjnt, snapctrl)
    cmds.setAttr(snapctrl[0]+'.visibility', 0)

    parentjnt = armResultJNT[prefix+'Lowerarm']
    copyctrl = armCTRL[prefix+'elbowIKLOC']
    newname = armCTRL[prefix+'elbowIKLOC']+'SnapTo'
    exists, snapctrl = CheckObjExists(newname)
    if exists:
        cmds.delete(snapctrl)
    snapctrl = cmds.duplicate(copyctrl, name = newname)
    existparent = cmds.listRelatives(snapctrl, parent = True)
    print(existparent)
    if existparent is None or not (existparent[0] is parentjnt):
        cmds.parent(snapctrl, parentjnt)
    cmds.setAttr(snapctrl[0]+'.visibility', 0)
    
    ##
    ## Stretch & Squash
    ##
    
    # stretch with IK arm control solver
    # total distance 

    switchCtrl = armCTRL[prefix+'Switch']
    attrname = 'stretch_toggle'
    exists = CheckAttributeExists(switchCtrl, attrname)
    if not exists:
        cmds.addAttr(switchCtrl, longName = attrname, niceName = 'Stretch Toggle', at = 'bool', dv = 1, k = True)
    
    print('## set up stretch and squash for IK arm')
    # create locator at the ik wrist
    locName = prefix+"wristLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(armIKJNT[prefix+'Wrist']), a = True) 
    cmds.xform(locNode, centerPivots = True)
         
    if cmds.listRelatives(locNode, p = True) == None or not cmds.listRelatives(locNode, p = True)[0] == IKConstGRP:
        cmds.parent(locNode, IKConstGRP)
        
    
    WristLocShape = cmds.listRelatives(locNode, shapes=True)[0]
 
    
    # create locator at the IK Upperarm JNT
    CreateGroupWithChild(armGRP[prefix+'IKConstGRP'], armIKJNT[prefix+'Upperarm'])

    locName = prefix+"UpperarmLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(armIKJNT[prefix+'Upperarm']), a = True) 
    cmds.xform(locNode, centerPivots = True)
        
    AddToGroup(armGRP[prefix+'IKConstGRP'], locNode)

    UpperarmLocShape = cmds.listRelatives(locNode, shapes=True)[0]
 
    
    distName = prefix+"armIKTotalLengthShape"
    exists, totalDistNode = CheckObjExists(distName)
    if not exists:
        totalDistNode = cmds.createNode('distanceDimShape', n = distName)   
        
    print (totalDistNode)
    
    pnode = cmds.listRelatives(totalDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, prefix+'armIKTotalLength', ignoreShape = True)
    lengthNodes.append(prefix+'armIKTotalLength')
    
     
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
        print ("Create New Curve : {}".format(animNode))
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = armStat[prefix+'LowerarmIKLength']) 
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Wrist'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = armStat[prefix+'LowerarmIKLength']*2)
        
    else:
        print ("Animation Curve Already exists")
    cmds.keyTangent(armIKJNT[prefix+'Wrist'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(armIKJNT[prefix+'Wrist']+'.translateX', poi = 'linear')
    
    animNode = 'lowerarm_' + prefix + 'IK_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve : {}".format(animNode))
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Lowerarm'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = armStat[prefix+'UpperarmIKLength']) 
        cmds.setDrivenKeyframe(armIKJNT[prefix+'Lowerarm'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = armStat[prefix+'UpperarmIKLength']*2)
    cmds.keyTangent(armIKJNT[prefix+'Lowerarm'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(armIKJNT[prefix+'Lowerarm']+'.translateX', poi = 'linear')
   
   
        
    ## counter rootScale effect
    nodename = prefix + 'IKUpperarm_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'lowerarm_' + prefix + 'IK_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    #CleanConnectionOnNode(armFKJNT[prefix+'Lowerarm'], 'translateX', False)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')



    
    
    nodename = prefix + 'IKLowerarm_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'wrist_' + prefix + 'IK_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    #CleanConnectionOnNode(armFKJNT[prefix+'Lowerarm'], 'translateX', False)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')
    
   
    ##  Elbow snap set up 
    # distance from elbow to Upperarm
    distName = prefix+"armElbowToUpperarmLengthShape"
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
    cmds.rename(pnode, prefix+"armElbowToUpperarmLength", ignoreShape = True)
    lengthNodes.append(prefix+"armElbowToUpperarmLength")
    
    
    # distance from elbow to wrist
    distName = prefix+"armElbowToWristLengthShape"
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
    cmds.rename(pnode, prefix+"armElbowToWristLength", ignoreShape = True)
    lengthNodes.append(prefix+"armElbowToWristLength")
    
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
    nodeName = prefix+"UpperarmElbowFKIK_Choice"
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

    # add arm xdir 
    mulName = 'elbow_'+prefix+'UpperarmDirX'
    exists,mulNode = CheckObjExists(mulName)
    if not exists:
        mulNode = cmds.createNode('multiplyDivide', n = mulName)
    cmds.setAttr(mulNode+'.operation', 1)
    CleanConnectionOnNode(blendNode, 'outputR', False)
    CleanConnectionOnNode(mulNode, 'input1X', True)
    cmds.connectAttr(blendNode+'.outputR', mulNode+'.input1X')
    cmds.setAttr(mulNode+'.input2X', armStat[prefix+'armXDir'])
    CleanConnectionOnNode(mulNode, 'outputX', False)


    bname = prefix+'arm_IKUpperarmStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(mulNode+'.outputX', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', armStat[prefix+'lowerarmTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)
    
    CleanConnectionOnNode(armIKJNT[prefix+'Lowerarm'], 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', armIKJNT[prefix+'Lowerarm'] + '.translateX')
    
    
    
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
    
        # add arm xdir 
    mulName = 'elbow_'+prefix+'LowerarmDirX'
    exists,mulNode = CheckObjExists(mulName)
    if not exists:
        mulNode = cmds.createNode('multiplyDivide', n = mulName)
    cmds.setAttr(mulNode+'.operation', 1)
    CleanConnectionOnNode(blendNode, 'outputR', False)
    CleanConnectionOnNode(mulNode, 'input1X', True)
    cmds.connectAttr(blendNode+'.outputR', mulNode+'.input1X')
    cmds.setAttr(mulNode+'.input2X', armStat[prefix+'armXDir'])
    CleanConnectionOnNode(mulNode, 'outputX', False)

    bname = prefix+'arm_IKLowerarmStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(mulNode+'.outputX', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', armStat[prefix+'wristTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)
    
    CleanConnectionOnNode(armIKJNT[prefix+'Wrist'], 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', armIKJNT[prefix+'Wrist'] + '.translateX')
    
     
    # elbow fk ik hybrid solution 
    # stretch with elbow FK -- TODO:? seems to be handled as elbow fk drives the ik bone 
    # add length attr to the elbow_Lowerarm_<prefix>_FK_JNT
    elbowctrl = 'elbow_lowerarm_{prefix}FK_JNT'.format(prefix = prefix)
    attr = 'length'
    exists = CheckAttributeExists(elbowctrl, attr)
    if not exists:
        cmds.addAttr(elbowctrl, longName = attr, attributeType = 'float', defaultValue = 1, k = True)

    animNode = elbowctrl+'_translateX'
    translateX = armStat[prefix+'wristTranslateX']
    print(animNode)
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ('create new curve')
        cmds.setDrivenKeyframe(armCTRL[prefix+ 'elbowFK_wrist'], attribute='translateX', currentDriver = elbowctrl+'.length', driverValue = 0, value = 0) 
        cmds.setDrivenKeyframe(armCTRL[prefix+'elbowFK_wrist'], attribute='translateX', currentDriver = elbowctrl+'.length', driverValue = 1, value = translateX)
        cmds.setAttr(elbowctrl+'.'+attr, 1)
        
    else:
        print('elbow wrist r fk anim curve already exists, skip creation')

    cmds.keyTangent(armCTRL[prefix+'elbowFK_wrist'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(armCTRL[prefix+'elbowFK_wrist']+'.translateX', poi = 'linear')

    
    # cleanup grps 
    grpname = armGRP[prefix+'IKConstGRP']
    for ln in lengthNodes:
        print(ln)
        AddToGroup(grpname, ln)
    
    return 0


# FKIK setup module
# link corresponding ik fk joint to result jnt 
# link the switch control blend attr with colorblender.blender attr    
def CreateBlendForJoint(jntList, jntName, blendAttr):
    # clean up for a more generic blending, jntlist[ij(input1), fj(input2), rj(output)], blenderAttr
    # jntname : the key for the dictionary: Lowerarm, Thigh ... etc 
    print('## [FKIK blend setup] :' + jntName)
   
    # create blend node for rotation
    kw = blendAttr.split('.')[-1] 
    print(kw)
    nodeNameRot = jntName + '_' + kw + 'Rot'
    exists, nodeRot = CheckObjExists(nodeNameRot)
    if not exists:    
        nodeRot = cmds.createNode('blendColors', n = nodeNameRot)
 
    ij = jntList[0]
    fj = jntList[1]
    rj = jntList[2]
    #break connection if it exists
    CleanConnectionOnNode(nodeNameRot, 'color1', True)
    cmds.connectAttr(ij + '.rotate', nodeNameRot + '.color1')  
    CleanConnectionOnNode(nodeNameRot, 'color2', True)
    cmds.connectAttr(fj + '.rotate', nodeNameRot + '.color2')   
    CleanConnectionOnNode(nodeNameRot, 'output', False)
    CleanConnectionOnNode(rj, 'rotate', True)
    cmds.connectAttr(nodeNameRot + '.output', rj + '.rotate')  
    CleanConnectionOnNode(nodeNameRot, 'blender', True)
    cmds.connectAttr(blendAttr, nodeNameRot + '.blender')
    
    
    #create blend node for translate
    nodeNameTran = jntName + '_' + kw + 'Tran'
    exists, nodetran = CheckObjExists(nodeNameTran)
    if not exists:    
        nodeRot = cmds.createNode('blendColors', n = nodeNameTran) 
    
    CleanConnectionOnNode(nodeNameTran, 'color1', True)    
    cmds.connectAttr(ij + '.translate', nodeNameTran + '.color1')
    CleanConnectionOnNode(nodeNameTran, 'color2', True) 
    cmds.connectAttr(fj + '.translate', nodeNameTran + '.color2')
    CleanConnectionOnNode(nodeNameTran, 'output', False)
    CleanConnectionOnNode(rj, 'translate', True)
    cmds.connectAttr(nodeNameTran + '.output', rj + '.translate')
    CleanConnectionOnNode(nodeNameTran, 'blender', True)
    cmds.connectAttr(blendAttr, nodeNameTran + '.blender')
 

    print("##[Link FK IK switch fnished!!]")
    
    return 1
    
    
def JointIKFKBlendSetup(isRight, partName):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'

    ResultDictionary = {}
    IKDictionary = {}
    FKDictionaty = {}
    CtrlDictionary = {}
    jointList = []

    if partName == 'arm':
        ResultDictionary = armResultJNT
        IKDictionary = armIKJNT
        FKDictionaty = armFKJNT
        CtrlDictionary = armCTRL
        jointList = ['Upperarm', 'Lowerarm', 'Wrist', 'Hand']
    elif partName == 'leg':
        ResultDictionary = legResultJNT
        IKDictionary = legIKJNT
        FKDictionaty = legFKJNT
        CtrlDictionary = legCTRL
        jointList = ['Thigh', 'Calf', 'Foot', 'Ball', 'Toe']
    else:
        print('##[ERROR] Invalid part name: {}, end setup!! '.format(partName))
        return 0
    
    # Duplicate resultjnt to fk jnt 
    fistJntName = FKDictionaty[prefix+jointList[0]]
    firstJnt = ResultDictionary[prefix+jointList[0]]
    cnodes = DuplicateJointChain(fistJntName, firstJnt, len(jointList)-1)
    print(cnodes)
    for dj in cnodes:
        splitnames = dj.split('_'+prefix)
        print(dj)
        if not ('GRP' in dj) and not ('SnapTo' in dj) and not ('GEO' in dj):
            if splitnames[0].title() in jointList:
                newname = FKDictionaty[prefix+splitnames[0].title()]
                #print(newname)
                cmds.rename(dj, newname)
            else:
                exists, node = CheckObjExists(dj)
                if exists:
                    cmds.delete(dj)
        else:
            exists, node = CheckObjExists(dj)
            if exists:
                cmds.delete(dj)

    # Duplicate resultjnt to ik jnt 
    fistJntName = IKDictionary[prefix+jointList[0]]
    firstJnt = ResultDictionary[prefix+jointList[0]]
    cnodes = DuplicateJointChain(fistJntName, firstJnt, len(jointList)-1)
    print(cnodes)
    for dj in cnodes:
        splitnames = dj.split('_'+prefix)
        print(splitnames)
        if not ('GRP' in dj) and not ('SnapTo' in dj) and not ('GEO' in dj):
            if splitnames[0].title() in jointList:
                newname = IKDictionary[prefix+splitnames[0].title()]
                cmds.rename(dj, newname)
            else:
                exists, node = CheckObjExists(dj)
                if exists:
                    cmds.delete(dj)
        else:
            exists, node = CheckObjExists(dj)
            if exists:
                cmds.delete(dj)

    #find the controller
    controlName = CtrlDictionary[prefix+'Switch']
    exists, switchNode = CheckObjExists(controlName)
    if not exists:
        print("[ERROR] please double check if the switch ctrl exists, end rigging process")
        return 0
    
    switchAttr = 'FKIK_blend'
    attrExist = cmds.attributeQuery(switchAttr, node=switchNode, exists=True)
    
    if not attrExist:
        cmds.addAttr(switchNode, ln = switchAttr, at = 'float', max = 1, min = 0, nn = 'FK/IK Blend', k = True)
 
    blendAttr = controlName + '.' + switchAttr
    for jn in ResultDictionary: 
        #print(jn) 
        if prefix in jn:
            jntName = jn
            rj = ResultDictionary[jntName]
            ij = IKDictionary[jntName]
            fj = FKDictionaty[jntName]
            # input order: connec to color1, color2, output
            jntList = [ij, fj, rj]
            # blend between FK IK joints
            CreateBlendForJoint(jntList, jntName, blendAttr)
    
        
    return 1
    

def ConnectArmToTorso(isRight):
    print('##[Connect] Arm to torso')
    
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_' 
    
    # pivot for all arm grps 
    armpivot = armResultJNT[prefix+'Upperarm']
    
    # create locator for arm translation, and fix it in the shoulderSpace group 
    locname = prefix+'arm_Translate_LOC'
    spaceGRP = partSpaceGRP['shoulder']
    exists, locNode = CheckObjExists(locname)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locname, p = getWSTranslate(armpivot), r = True) 
    cmds.xform(locNode, centerPivots = True)
        
    if cmds.listRelatives(locNode, p = True) == None or not cmds.listRelatives(locNode, p = True)[0] == spaceGRP:
        cmds.parent(locNode, spaceGRP)
    cmds.setAttr(locNode[0]+'.visibility', 0)
    
    
    orientTargets = []
    
    # create locators for arm orientation shoulderSpace, bodySpace, rootSpace
    locindex = ['shoulder', 'body', 'root']
    for l in locindex:
        locname = prefix+'arm_'+l+'SpaceRotate_LOC'
        spaceGRP = partSpaceGRP[l]
        exists, locNode = CheckObjExists(locname)
        if exists:
            cmds.delete(locNode)
        locNode = cmds.spaceLocator(n = locname, p = getWSTranslate(armpivot), a = True) 
        cmds.xform(locNode, centerPivots = True)          
        if cmds.listRelatives(locNode, p = True) == None or not cmds.listRelatives(locNode, p = True)[0] == spaceGRP:
            cmds.parent(locNode, spaceGRP)
        cmds.setAttr(locNode[0]+'.visibility', 0)
        orientTargets.append(locNode[0])
    
    
    # point IKConst_GRP, FKConst_GRP, resultConst_GRP with tanslate_LOC
    grplist = [armGRP[prefix+'IKConstGRP'], armGRP[prefix+'FKConstGRP'], armGRP[prefix+'ResultConstGRP']]
    for grp in grplist:
        constraint = cmds.pointConstraint(prefix+'arm_Translate_LOC', grp, name = prefix+grp+'_FollowPointConstraint')
    
    
    
    # create arm follow attr on the fk Upperarm ctrl 
    objname = armCTRL[prefix+'UpperarmCtrl']
    attrname = 'orient_follow_space'
    exists = CheckAttributeExists(objname, attrname)
    if not exists:
        cmds.addAttr(objname, longName = attrname, niceName = 'Orient Follow Space', attributeType = 'enum', enumName = 'Shoulder:Upperbody:Root', k = True)   
    
    # orient FKConst_GRP, resultConst_GRP with shoulderSpace, bodySpace and RootSpace
    grp = armGRP[prefix+'FKConstGRP']
    constraint = cmds.orientConstraint(orientTargets, grp, name = prefix+grp+'_FollowOrientConstraint')[0]
    index = 0
    for loc in orientTargets: 
        attr = '{0}W{1}'.format(loc,index)
        cmds.delete(constraint, at = attr, e = True)
        expname = grp+'_'+attr+'_OrientExpression'
        exists, exp = CheckObjExists(expname)
        if exists:
            print("##delete current exp {}".format(exp))
            cmds.delete(exp)
        
        expstring = "if({targetAttr} == {index}){{{constraint}.{at} = 1;}}else{{{constraint}.{at} = 0;}}".format(targetAttr = objname+'.'+attrname, constraint = constraint, at = attr, index = index)
        index = index + 1
        #print(expstring)
        cmds.expression(o = constraint, s = expstring, ae = True, n = expname) 
        
        
    grp = armGRP[prefix+'ResultConstGRP']
    constraint = cmds.orientConstraint(orientTargets, grp, name = prefix+grp+'_FollowOrientConstraint')[0]
    index = 0
    for loc in orientTargets: 
        attr = '{0}W{1}'.format(loc,index)
        cmds.delete(constraint, at = attr, e = True)
        expname = grp+'_'+attr+'_OrientExpression'
        exists, exp = CheckObjExists(expname)
        if exists:
            print("##delete current exp {}".format(exp))
            cmds.delete(exp)
        
        expstring = "if({targetAttr} == {index}){{{constraint}.{at} = 1;}}else{{{constraint}.{at} = 0;}}".format(targetAttr = objname+'.'+attrname, constraint = constraint, at = attr, index = index)
        index = index + 1
        #print(expstring)
        cmds.expression(o = constraint, s = expstring, ae = True, n = expname) 
    
    CleanConnectionOnNode(armGRP[prefix+'ResultConstGRP'] ,'rotate',True)
    CleanConnectionOnNode(armGRP[prefix+'ResultConstGRP'] ,'rotateX',True)
    CleanConnectionOnNode(armGRP[prefix+'ResultConstGRP'] ,'rotateY',True)
    CleanConnectionOnNode(armGRP[prefix+'ResultConstGRP'] ,'rotateZ',True)

    # Choice for orient ResultConst_GRP: IK follow IKConstGRP, FK follow choice of space?
    bname = prefix+'arm_resultConstGRPOreintChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    constraint = prefix+armGRP[prefix+'ResultConstGRP']+'_FollowOrientConstraint'
    IKOrient = armGRP[prefix+'IKConstGRP']
    CleanConnectionOnNode(bnode, 'color1', True)    
    cmds.connectAttr(IKOrient + '.rotate', bnode + '.color1')
    CleanConnectionOnNode(bnode, 'color2', True) 
    cmds.connectAttr(constraint + '.constraintRotate', bnode + '.color2')
    CleanConnectionOnNode(bnode, 'output', False)
    cmds.connectAttr(bnode + '.output', armGRP[prefix+'ResultConstGRP'] + '.rotate')
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(armCTRL[prefix+'Switch']+'.FKIK_blend', bnode + '.blender')
    
    print('##[Finished] Arm successfully connected to torso')
    return 1
    
###################
# Match FK & IK 
###################

def debugPrintPos():
    ArmInitJointNames(True)
    jntlist = ['Upperarm', 'Lowerarm', 'Wrist']
    prefix = 'r_'
    for jn in jntlist:
        fkjnt = armFKJNT[prefix+jn]
        snapjnt = armFKJNT[prefix+jn]+'SnapTo'
        print("[Debug] {0} ws rot is {1}, {2} ws rot is {3}".format(fkjnt, getWSRotate(fkjnt),
                snapjnt, getWSRotate(snapjnt)))


# IK >>>> FK
def ArmMatchFK2IK(isright):
    if isright:
        prefix = 'r_'
    else:
        prefix = 'l_'
    print ('####### BEFORE MATCH ########')
    #debugPrintPos()
    # set rot of FK to match result joints in IK mode, TODO what if under different translation space? is the snap jnt necessary?
    # TODO: if execute xform in for loop only the first rot is evaluated correctly? 
    cmds.xform(armCTRL[prefix+'gimbleCtrl'], ro = (0,0,0), ws = True) 
    
    fkjnt = armFKJNT[prefix+'Upperarm']
    snapjnt = armFKJNT[prefix+'Upperarm']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

    fkjnt = armFKJNT[prefix+'Lowerarm']
    snapjnt = armFKJNT[prefix+'Lowerarm']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

    fkjnt = armFKJNT[prefix+'Wrist']
    snapjnt = armFKJNT[prefix+'Wrist']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True) 
  
    # match fk arm lenght to ik 
    elbowctrl = armCTRL[prefix+'elbowIKCtrl']
    elbowsnap = cmds.getAttr(elbowctrl + '.elbow_snap')
    upperStretchRatio = 1
    lowerStretchRatio = 1
    if elbowsnap == 0:
        # use the seperate length 
        totaldist = cmds.getAttr(prefix+'armIKTotalLengthShape'+'.distance')
        upperStretchRatio = totaldist / armStat[prefix+'IKtotalLength'] 
        lowerStretchRatio = totaldist / armStat[prefix+'IKtotalLength'] 
    elif elbowsnap == 1:
        # use total length 
        upperdist = cmds.getAttr(prefix+'armElbowToUpperarmLengthShape'+'.distance')
        print(upperdist)
        lowerdist = cmds.getAttr(prefix+'armElbowToWristLengthShape'+'.distance')
        upperStretchRatio = upperdist / armStat[prefix+'UpperarmIKLength'] 
        lowerStretchRatio = lowerdist / armStat[prefix+'LowerarmIKLength'] 
    else:
        print("elbow snap is between 0-1, should we blend the length? ")

    print("## Upperarm ratio is {0} ; Lowerarm ratio is {1}".format(upperStretchRatio, lowerStretchRatio))
    cmds.setAttr(armCTRL[prefix+'UpperarmCtrl'] + '.length' , upperStretchRatio)
    cmds.setAttr(armCTRL[prefix+'LowerarmCtrl'] + '.length' , lowerStretchRatio)



    print ('####### AFTER MATCH ########')
    #debugPrintPos()
    
    #reset gimble correction node 
       
    cmds.setAttr(armCTRL[prefix+'Switch'] + '.FKIK_blend', 0)
    
#left arm switch to IK 
# FK >>>> IK
def ArmMatchIK2FK(isright):
    if isright:
        prefix = 'r_'
        isForeArmFK = isMatchingRightFKForearm
    else:
        prefix = 'l_'
        isForeArmFK = isMatchingLeftFKForearm

    # matching position 
    elbowctrl = armCTRL[prefix+'elbowIKCtrl']
    elbowjnt = armResultJNT[prefix + 'Lowerarm']
    ikpivot = getWRPivot(elbowctrl)
    snappivot = getWRPivot(elbowjnt)
    rootOffset = getWSTranslate(centralCTRL['rootCtrl'])
    
    newt = getWSTranslate(elbowjnt)
    cmds.xform(elbowctrl, t = newt, ws = True) 

    if not isForeArmFK:
        ikctrl = armCTRL[prefix+'armIKCtrl'] 
        defaultctrl = armCTRL[prefix+'armIKCtrl'] + 'Default'
        snapctrl = armCTRL[prefix+'armIKCtrl'] + 'SnapTo'
        print(snapctrl)
        defaultpivot = getWRPivot(defaultctrl)
        snappivot = getWRPivot(snapctrl) 
        deltapivot = getVectorMinus(snappivot, defaultpivot)
        finalposition = getVectorMinus(deltapivot, rootOffset)
        #print('Before match: {0} translation is {1}, {2} translation is {3}'.format(
        #    ikctrl, getWSTranslate(ikctrl), snapctrl, getWSTranslate(snapctrl)
        #))
        cmds.xform(ikctrl, t = finalposition, ws = True)
        #print('After match: {0} translation is {1}, {2} translation is {3}'.format(
        #    ikctrl, getWSTranslate(ikctrl), snapctrl, getWSTranslate(snapctrl)
        #))

        #print('Before match: {0} rotation is {1}, {2} rotation is {3}'.format(
        #    ikctrl, getWSRotate(ikctrl), snapctrl, getWSRotate(snapctrl)
        #))
        cmds.xform(ikctrl, ro = getWSRotate(snapctrl), ws = True)

        #print('After match: {0} rotation is {1}, {2} rotation is {3}'.format(
        #    ikctrl, getWSRotate(ikctrl), snapctrl, getWSRotate(snapctrl)
        #))
        cmds.setAttr(elbowctrl + '.elbow_snap', 0)
        cmds.setAttr(elbowctrl + '.elbow_fkik_blend', 1)
    else:
        # elbow Lowerarm 
        fkjnt = armCTRL[prefix+'elbowFK_Lowerarm']
        snapjnt = armFKJNT[prefix+'Lowerarm']+'SnapTo'
        print(fkjnt)
        cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

        #elbow wrist
        fkjnt = armCTRL[prefix+'elbowFK_wrist']
        snapjnt = armFKJNT[prefix+'Wrist']+'SnapTo'
        print(fkjnt)
        cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

        cmds.setAttr(elbowctrl + '.elbow_snap', 1)
        cmds.setAttr(elbowctrl + '.elbow_fkik_blend', 0)
    
    # match ik length
     #match arm length 
    curUpperarmDist = cmds.getAttr(armFKJNT[prefix + 'Lowerarm']+ '.translateX')
    curLowerarmDist = cmds.getAttr(armFKJNT[prefix + 'Wrist']+ '.translateX')
    defaultUpperarmDist = armStat[prefix+'lowerarmTranslateX']
    defaultLowerarmDist = armStat[prefix+'wristTranslateX']

    if not isForeArmFK:
        if abs(curUpperarmDist - defaultUpperarmDist) > 0.002 or abs(curLowerarmDist - defaultLowerarmDist) > 0.002 : 
            # enable ik arm elbow snap 
            cmds.setAttr(armCTRL[prefix + 'elbowIKCtrl'] + '.elbow_snap', 1)
            print ('## FK >>> IK, matching length, enable elbow snap')
        else:
            cmds.setAttr(armCTRL[prefix + 'elbowIKCtrl'] + '.elbow_snap', 0)
            print ('## FK >>> IK, matching length, enable elbow snap')
    else:
        # elbow_snap should be on 1 by default in this mode 
        print ('## FK >>> IK, matching length, use FK forearm elbow snap')
        # change the length attr on the elbowFL_Lowerarm
        elbowLowerarm = armCTRL[prefix+'elbowFK_Lowerarm']
        stretchratio = curLowerarmDist/defaultLowerarmDist
        cmds.setAttr(elbowLowerarm + '.length', stretchratio)

    
    cmds.setAttr(armCTRL[prefix+'Switch'] + '.FKIK_blend', 1)
    
###################
# Leg rig setup 
###################

# FK leg
def ConfigureFKLeg(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'
    ## code stats here
    print('##[LEG FK] Create Ctrls for FK joints')
    switchCtrl = legCTRL[prefix+'Switch']
    attrname = 'stretch_toggle'
    exists = CheckAttributeExists(switchCtrl, attrname)
    if not exists:
        cmds.addAttr(switchCtrl, longName = attrname, niceName = 'Stretch Toggle', at = 'bool', dv = 1, k = True)

    for jn in legFKJNT:
        print(jn) 
        if (prefix in jn) and (not '_Toe' in jn):
            # create control curves and attach to the joint 
            CreateContorlCurvesAndParentTo(jn, legFKJNT, (0,1,0))
            # link ctrls visibility with fkik switch 
            cmds.delete(legFKJNT[jn], at = 'visibility', e = True)
            name = jn + 'FKIKVisibility_expression'
            exists, expnode = CheckObjExists(name)
            if exists:
                cmds.delete(expnode)
            expstring = "if({switchCtrl}.FKIK_blend == 1){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(switchCtrl = switchCtrl, jname = legFKJNT[jn])
            print(expstring)
            cmds.expression(o = legFKJNT[jn], s = expstring, ae = True, n = name)
        #end prefix check 
    #end setup for each joint  

    # create snapto jnt for fkik match 
    ## setup snap jnts 
    jntlist = ['Thigh', 'Calf', 'Foot', 'Ball']
    for jn in jntlist:
        parentjnt = legResultJNT[prefix+jn]
        copyjnt = legFKJNT[prefix+jn]
        newname = legFKJNT[prefix+jn]+'SnapTo'
        exists, snapjnt = CheckObjExists(newname)
        if exists:
            cmds.delete(snapjnt)
        snapjnt = cmds.duplicate(copyjnt, name = newname, parentOnly = True)
        existparent = cmds.listRelatives(snapjnt, parent = True)
        if existparent == None or not (existparent[0] is parentjnt):
            cmds.parent(snapjnt, parentjnt)
        existshape = cmds.listRelatives(snapjnt, shapes = True)
        if not (existshape == None) and len(existshape) > 0:
            cmds.delete(snapjnt, shapes = True)
        cmds.setAttr(snapjnt[0]+'.visibility', 0)

    print("##[FINISHED] leg SnapTo joints setup success!")

    # setup FK leg stretch & squash
    print('## setting up FK ARM stretch & squash')
    #adding stretch&squash function to FK arm joint
    nname = legCTRL[prefix+'ThighFK']
    attr = 'length'
    translateX = legStat[prefix+'calfTranslateX']
    if not CheckAttributeExists(nname, attr):
        print('## Create length attr for ctrl')
        cmds.addAttr(nname, ln = attr, at = 'float', nn = 'Length', k = True, dv = 1)
        #check if there is a key on the attribute 
    
    animNode = legCTRL[prefix+'CalfFK']+'_translateX'
    print(animNode)
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve {}".format(animNode))
        cmds.setDrivenKeyframe(legFKJNT[prefix+'Calf'], attribute='translateX', currentDriver = nname+'.length', driverValue = 0, value = 0)
        cmds.setDrivenKeyframe(legFKJNT[prefix+'Calf'], attribute='translateX', currentDriver = nname+'.length', driverValue = 1, value = translateX)
    else:
        print('{} curve exists, skip creation'.format(animNode))
    # update the animation curve 
    cmds.setAttr(nname+'.'+attr, 1)
    cmds.keyTangent(legFKJNT[prefix+'Calf'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legFKJNT[prefix+'Calf']+'.translateX', poi = 'linear')

    # add stretch toggle 
    animNode = legCTRL[prefix+'CalfFK']+'_translateX'
    bname = prefix+'leg_ThighStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(legFKJNT[prefix+'Thigh']+'.length', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', 1)
    CleanConnectionOnNode(animNode, 'input', True)
    CleanConnectionOnNode(bnode, 'outputR', False)
    cmds.connectAttr(bnode+'.outputR', animNode+'.input')
          
    
    nname = legCTRL[prefix+'CalfFK']
    attr = 'length'
    translateX = legStat[prefix+'footTranslateX']
    if not CheckAttributeExists(nname, attr):
        print('## Create length attr for ctrl')
        cmds.addAttr(nname, ln = attr, at = 'float', nn = 'Length', k = True, dv = 1)
        #check if there is a key on the attribute 
        
    animNode = legCTRL[prefix+'FootFK'] + '_translateX'
    print(animNode)
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ('create new curve')
        cmds.setDrivenKeyframe(legFKJNT[prefix+'Foot'], attribute='translateX', currentDriver = nname+'.length', driverValue = 0, value = 0) 
        cmds.setDrivenKeyframe(legFKJNT[prefix+'Foot'], attribute='translateX', currentDriver = nname+'.length', driverValue = 1, value = translateX)
    else:
        print('{} curve exists, skip creation'.format(animNode))
    cmds.setAttr(nname+'.'+attr, 1)
    cmds.keyTangent(legFKJNT[prefix+'Foot'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legFKJNT[prefix+'Foot']+'.translateX', poi = 'linear')

    animNode = legCTRL[prefix+'FootFK']+'_translateX'
    bname = prefix+'leg_CalfStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(legFKJNT[prefix+'Calf']+'.length', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', 1)
    CleanConnectionOnNode(animNode, 'input', True)
    CleanConnectionOnNode(bnode, 'outputR', False)
    cmds.connectAttr(bnode+'.outputR', animNode+'.input')

    print("##[FINISHED] leg Stretch & Squash setup success!")

    # create fk group 
    grpname = legGRP[prefix+'FKConstGRP']
    grpchild = legFKJNT[prefix+'Thigh']
    CreateGroupWithChild(grpname, grpchild)

    print("##[FINISHED] leg FK group setup success!")

    return 1

# IK leg 
def ConfigureIKLeg(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'
    ## code stats here
    print ('## set up Auto (noflip) & Manual Knee dual solution')
    lengthNodes = []
    IKCtrl = legCTRL[prefix+'FootIK']
    exists, ctrlNode = CheckObjExists(IKCtrl)
    if not exists:
        # TODO: create ctrl and place it at a proximit pos
        print('## [WARNING] {} doesn\'t exitsts in thr current scene, creating a default one for now!')
        return 0

    # stretch toggle 
    switchCtrl = legCTRL[prefix+'Switch']
    attrname = 'stretch_toggle'
    exists = CheckAttributeExists(switchCtrl, attrname)
    if not exists:
        cmds.addAttr(switchCtrl, longName = attrname, niceName = 'Stretch Toggle', at = 'bool', dv = 1, k = True)

    # create snapTo ctrl for ikctrl 
    snapname = IKCtrl + 'SnapTo'
    exists, snapctrl = CheckObjExists(snapname)
    if exists:
        cmds.delete(snapctrl)
    snapctrl = cmds.duplicate(IKCtrl, ic = False, name = snapname, parentOnly = True)
    AddToGroup(legResultJNT[prefix+'Foot'], snapctrl)

    defaultname = IKCtrl + 'Default'
    exists, defaultctrl = CheckObjExists(defaultname)
    if exists:
        cmds.delete(defaultctrl)
    defaultctrl = cmds.duplicate(IKCtrl, ic = False, name = defaultname, parentOnly = True)
    
    attrName = 'manual_auto_blend'
    exists = CheckAttributeExists(IKCtrl, attrName)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attrName, niceName = 'Manual/Auto Knee Blend', min = 0, max = 1, at = 'float', dv = 1, k = True) 
    
    # set up visibility control 
    cmds.delete(IKCtrl, at = 'visibility', e = True)
    name = IKCtrl + 'FKIKVisibility_expression'
    switchCtrl = legCTRL[prefix+'Switch']
    exists, expnode = CheckObjExists(name)
    if exists:
        cmds.delete(expnode)
    expstring = "if({switchCtrl}.FKIK_blend == 1){{{jname}.visibility = 1;}}else{{{jname}.visibility = 0;}}".format(switchCtrl = switchCtrl, jname = IKCtrl)
    print(expstring)
    cmds.expression(o = IKCtrl, s = expstring, ae = True, n = name)


    # duplicate ik joints from thigh to foot
    targetJntName = ['Thigh', 'Calf', 'Foot']

    fistJntName = legIKJNT[prefix+'ThighAuto']
    firstJnt = legIKJNT[prefix+'Thigh']
    cnodes = DuplicateJointChain(fistJntName, firstJnt, 2)
    print(cnodes)
    for dj in cnodes:
        splitnames = dj.split('_'+prefix)
        print(splitnames[0])
        if not 'effector' in splitnames[0]:
            if splitnames[0].title() in targetJntName:
                newname = legIKJNT[prefix+splitnames[0].title()+'Auto']
                cmds.rename(dj, newname)
            else:
                exists, node = CheckObjExists(dj)
                if exists:
                    cmds.delete(dj)

    

    fistJntName = legIKJNT[prefix+'ThighManual']
    firstJnt = legIKJNT[prefix+'Thigh']
    cnodes = DuplicateJointChain(fistJntName, firstJnt, 2)
    print(cnodes)
    for dj in cnodes:
        splitnames = dj.split('_'+prefix)
        print(splitnames[0])
        if not 'effector' in splitnames[0]:
            if splitnames[0].title() in targetJntName:
                newname = legIKJNT[prefix+splitnames[0].title()+'Manual']
                cmds.rename(dj, newname)
            else:
                exists, node = CheckObjExists(dj)
                if exists:
                    cmds.delete(dj)


    # set up blend between two joint chains 
    for jn in targetJntName:
        jname = prefix+jn
        jntList = [legIKJNT[jname+'Auto'], legIKJNT[jname+'Manual'],legIKJNT[jname]]
        blendAttr = IKCtrl + '.' + attrName
        # create Manual and Auto blend
        CreateBlendForJoint(jntList, jname, blendAttr)


    ## IK leg Jnt prep finihsed 

    ########## ---------------------------------- ##################
    ## Start Auto & Manual knee set up 
    print ('## Setup leg IK solvers, footIK, ballIK, toeIK')

    startjnt = legIKJNT[prefix+'ThighManual']
    endjnt = legIKJNT[prefix+'FootManual']
    # footIK Manual Knee set up, with pull vector knee 
    hdlname = legHDL[prefix+'KneeManual']
    exists, manualHDL = CheckObjExists(hdlname)
    if not exists:
        manualHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikRPsolver', sticky = 'sticky')[0]
    
    # add pull vector - manual 
    locName = prefix+"KneeIKManual_LOC"
    exists, locNode = CheckObjExists(locName)
    offset = [0,0,gSceneScale * 2]
    jointPos = getWSTranslate(legIKJNT[prefix+'Calf'])
    position = getVectorAdd(jointPos, offset)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = position, a = True) [0]
    cmds.xform(locNode, centerPivots = True)
    manualLoc = locNode

    manualCtrl = legCTRL[prefix+'KneeIKManual']
    exists, mCtrl = CheckObjExists(manualCtrl)
    if not exists:
        print('##[WARNING] {} is not found, please create it!'.format(manualCtrl))
        return 0
    # move manualctrl to the loc position 
    cmds.xform(manualCtrl, t = position, ws = True)
    # add expression to the manual ctrl visibility
    cmds.delete(manualCtrl, at = 'visibility', e = True)
    name = manualCtrl + 'ManualAutoVisibility_expression'
    switchCtrl = legCTRL[prefix+'Switch']
    exists, expnode = CheckObjExists(name)
    if exists:
        cmds.delete(expnode)
    expstring = "if(({kneeCtrl}.manual_auto_blend == 1) || ({switchCtrl}.FKIK_blend == 0)){{{jname}.visibility = 0;}}else{{{jname}.visibility = 1;}}".format(switchCtrl = switchCtrl, kneeCtrl = IKCtrl, jname = manualCtrl)
    print(expstring)
    cmds.expression(o = manualCtrl, s = expstring, ae = True, n = name)

    # create pole vector for the manual knee
    pvname = 'leg_{prefix}_KneeIKManual_PVConstraint'.format(prefix=prefix)
    exist, pvconstraint = CheckObjExists(pvname)
    if exists:
        cmds.delete(pvconstraint)
    cmds.poleVectorConstraint(manualLoc, manualHDL, name = pvname)

    curparent = cmds.listRelatives(manualLoc, parent = True)
    if curparent == None or curparent != manualCtrl:
        cmds.parent(manualLoc, manualCtrl)
    cmds.setAttr(manualLoc + '.visibility', 0)

    ########## ---------------------------------- ##################
    # add pole vector - auto, no flip knee
    locName = prefix+"KneeIKAuto_LOC"
    exists, locNode = CheckObjExists(locName)
    offset = [0,0,gSceneScale * 2]
    jointPos = getWSTranslate(legIKJNT[prefix+'Calf'])
    position = getVectorAdd(jointPos, offset)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName,  a = True) [0]
    
    autoLoc = locNode
    cmds.xform(autoLoc, t = position, ws = True)
    autoGrpName = legCTRL[prefix+'KneeIKAuto']
    exists, autoGRP = CheckObjExists(autoGrpName)
    if not exists:
        print('##[WARNING] {} is not found, please create it!'.format(autoGrpName))
        autoGRP = cmds.group(name = autoGrpName, em = True)

    

    startjnt = legIKJNT[prefix+'ThighAuto']
    endjnt = legIKJNT[prefix+'FootAuto']
    # footIK Manual Knee set up, with pull vector knee 
    hdlname = legHDL[prefix+'KneeAuto']
    exists, autoHDL = CheckObjExists(hdlname)
    if not exists:
        autoHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikRPsolver', sticky = 'sticky')[0]
    
    pvname = 'leg_{prefix}_KneeIKAuto_PVConstraint'.format(prefix=prefix)
    exist, pvconstraint = CheckObjExists(pvname)
    if exists:
        cmds.delete(pvconstraint)
    cmds.poleVectorConstraint(autoLoc, autoHDL, name = pvname)


    # move to new position and adjust the twist attribute on the autoHDL
    jntpos = getWSTranslate(legIKJNT[prefix+'FootAuto'])
    offset = [-gSceneScale*3, 0, 0]
    newposition = getVectorAdd(jntpos, offset)
    cmds.xform(autoLoc, t = newposition, ws = True)
    cmds.xform(locNode, centerPivots = True)
    CleanConnectionOnNode(autoHDL, 'twist', True)
    cmds.setAttr(autoHDL + '.twist', legStat[prefix+'defaultKneeTwist'])

    cmds.setAttr(autoLoc + '.visibility', 0)
    AddToGroup(autoGRP, autoLoc)
    # Add twist attribute on the foot ik ctrl 
    
    # link the twist attr on hdl to foot IK ctrl
    attrName = 'knee_twist'
    exists = CheckAttributeExists(IKCtrl,attrName)
    if not exists:
        cmds.addAttr(IKCtrl, at = 'float', longName = attrName, niceName = 'Auto Knee Twist', dv = 0, k = True)
    
    CleanConnectionOnNode(autoGRP, 'translateZ', True)
    cmds.setAttr(IKCtrl+'.'+attrName, 0)
    cmds.connectAttr(IKCtrl+'.'+attrName, autoGRP + '.translateZ')

    # parent both knee control grps under foot IK ctrl 
    # create empty foot hdl grp 
    grpname = legGRP[prefix+'footHDL']
    exists, grp = CheckObjExists(grpname)
    if not exists:
        grp = cmds.group(name = grpname, em = True, w = True)
    cmds.xform(grp, t = getWSTranslate(legIKJNT[prefix+'Foot']), ws = True)

    AddToGroup(IKCtrl, grp)
    AddToGroup(grp, manualHDL)
    AddToGroup(grp, autoHDL)
    AddToGroup(IKCtrl, autoGRP)

    # create IKconst GRP
    grpname = legGRP[prefix + 'IKConstGRP']
    child = legIKJNT[prefix + 'Thigh']
    CreateGroupWithChild(grpname, child)
    AddToGroup(grpname, legIKJNT[prefix+'ThighManual'])
    AddToGroup(grpname, legIKJNT[prefix+'ThighAuto'])


    ########## ---------------------------------- ##################
    # IK stretch & squash setup
    print('## set up stretch and squash for IK leg')
    ## create length locators 
    # create locator at ik foot
    IKCtrl = legCTRL[prefix + 'FootIK']
    locName = prefix+"footLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(legIKJNT[prefix+'Foot']), a = True) 
    cmds.xform(locNode, centerPivots = True)
    cmds.setAttr(locNode[0] + '.visibility', 0)
    AddToGroup(IKCtrl,locNode)
    FootLocShape = cmds.listRelatives(locNode, shapes=True)[0]

    # create upper_length and lower_length attr to control ununifrom stretch 
    attr = 'upper_length'
    exists = CheckAttributeExists(IKCtrl, attr)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attr, niceName = 'Upperleg Length', at = 'float', min = 0, k = True, dv = 1)

    attr = 'lower_length'
    exists = CheckAttributeExists(IKCtrl, attr)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attr, niceName = 'Lowerleg Length', at = 'float', min = 0, k = True, dv = 1)
 
    
    # create locator at IK thigh JNT
    locName = prefix+"thighLength_LOC"
    exists, locNode = CheckObjExists(locName)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locName, p = getWSTranslate(legIKJNT[prefix+'Thigh']), a = True) 
    cmds.xform(locNode, centerPivots = True)
    cmds.setAttr(locNode[0] + '.visibility', 0)
    AddToGroup(legGRP[prefix+'IKConstGRP'], locNode)
    ThighLocShape = cmds.listRelatives(locNode, shapes=True)[0]
 
    
    distName = prefix+"legIKTotalLengthShape"
    exists, totalDistNode = CheckObjExists(distName)
    if not exists:
        totalDistNode = cmds.createNode('distanceDimShape', n = distName)   
    pnode = cmds.listRelatives(totalDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, prefix+'legIKTotalLength', ignoreShape = True)
    lengthNodes.append(prefix+'legIKTotalLength')
    
     
    p1 = FootLocShape
    p2 = ThighLocShape
    CleanConnectionOnNode(totalDistNode, 'startPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', totalDistNode + '.startPoint')
    CleanConnectionOnNode(totalDistNode, 'endPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', totalDistNode + '.endPoint')
    defaultDistance = cmds.getAttr(totalDistNode+'.distance')

    ## key distance with joint position 
    print(defaultDistance)
    animNode = 'foot_' + prefix + 'IK_Auto_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve")
        cmds.setDrivenKeyframe(legIKJNT[prefix+'FootAuto'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = legStat[prefix+'footTranslateX']) 
        cmds.setDrivenKeyframe(legIKJNT[prefix+'FootAuto'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = legStat[prefix+'footTranslateX']*2)
    else:
        print ("Animation Curve Already exists")
    cmds.keyTangent(legIKJNT[prefix+'FootAuto'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legIKJNT[prefix+'FootAuto']+'.translateX', poi = 'linear')

    animNode = 'calf_' + prefix + 'IK_Auto_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        cmds.setDrivenKeyframe(legIKJNT[prefix+'CalfAuto'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = legStat[prefix+'calfTranslateX']) 
        cmds.setDrivenKeyframe(legIKJNT[prefix+'CalfAuto'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = legStat[prefix+'calfTranslateX']*2)
    else:
        print ("Animation Curve Already exists")
    cmds.keyTangent(legIKJNT[prefix+'CalfAuto'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legIKJNT[prefix+'CalfAuto']+'.translateX', poi = 'linear')
   
   
        
    ## counter rootScale effect
    nodename = prefix + 'IKThighAuto_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'calf_' + prefix + 'IK_Auto_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')

    mulname = prefix + 'IKThighAuto_Stretch_LengthMul'
    thighAuto = legIKJNT[prefix+'CalfAuto']
    exists, mulnode = CheckObjExists(mulname)
    if not exists:
        mulnode = cmds.createNode('multiplyDivide', name = mulname)
    
    cmds.setAttr(mulnode+'.operation', 1)
    CleanConnectionOnNode(mulnode, 'input1X', True)
    cmds.connectAttr(animNode+'.output', mulnode+'.input1X')
    CleanConnectionOnNode(mulnode, 'input2X', True)
    cmds.connectAttr(IKCtrl+'.upper_length', mulnode+'.input2X')
    CleanConnectionOnNode(mulnode, 'outputX', False)

    # Auto ik leg stretch toggle 
    bname = prefix+'leg_IKAutoThighStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(mulnode+'.outputX', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', legStat[prefix+'calfTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)

    CleanConnectionOnNode(thighAuto, 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', thighAuto+'.translateX')

    
    nodename = prefix + 'IKCalfAuto_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'foot_' + prefix + 'IK_Auto_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')

    mulname = prefix + 'IKCalfAuto_Stretch_LengthMul'
    calfAuto = legIKJNT[prefix+'FootAuto']
    exists, mulnode = CheckObjExists(mulname)
    if not exists:
        mulnode = cmds.createNode('multiplyDivide', name = mulname)
    
    cmds.setAttr(mulnode+'.operation', 1)
    CleanConnectionOnNode(mulnode, 'input1X', True)
    cmds.connectAttr(animNode+'.output', mulnode+'.input1X')
    CleanConnectionOnNode(mulnode, 'input2X', True)
    cmds.connectAttr(IKCtrl+'.lower_length', mulnode+'.input2X')
    CleanConnectionOnNode(mulnode, 'outputX', False)

    # Auto ik leg stretch toggle 
    bname = prefix+'leg_IKAutoCalfStretchChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(mulnode+'.outputX', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', legStat[prefix+'footTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)

    CleanConnectionOnNode(calfAuto, 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', calfAuto+'.translateX')

    # Manual knee
    animNode = 'foot_' + prefix + 'IK_Manual_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        print ("Create New Curve")
        cmds.setDrivenKeyframe(legIKJNT[prefix+'FootManual'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = legStat[prefix+'footTranslateX']) 
        cmds.setDrivenKeyframe(legIKJNT[prefix+'FootManual'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = legStat[prefix+'footTranslateX']*2)
    else:
        print ("Animation Curve Already exists")
    cmds.keyTangent(legIKJNT[prefix+'FootManual'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legIKJNT[prefix+'FootManual']+'.translateX', poi = 'linear')

    animNode = 'calf_' + prefix + 'IK_Manual_JNT_translateX'
    exists, node = CheckObjExists(animNode)
    if not exists:
        cmds.setDrivenKeyframe(legIKJNT[prefix+'CalfManual'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance, value = legStat[prefix+'calfTranslateX']) 
        cmds.setDrivenKeyframe(legIKJNT[prefix+'CalfManual'], attribute='translateX', currentDriver = totalDistNode+'.distance', driverValue = defaultDistance*2, value = legStat[prefix+'calfTranslateX']*2)
    else:
        print ("Animation Curve Already exists")
    cmds.keyTangent(legIKJNT[prefix+'CalfManual'], attribute='translateX', itt = 'spline', ott = 'spline')
    cmds.setInfinity(legIKJNT[prefix+'CalfManual']+'.translateX', poi = 'linear')
   
   
        
    ## counter rootScale effect
    nodename = prefix + 'IKThighManual_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'calf_' + prefix + 'IK_Manual_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')
    
    
    nodename = prefix + 'IKCalfManual_Stretch_RootScaleDiv'
    exists, rootScaleDiv = CheckObjExists(nodename)
    print(rootScaleDiv)
    if not exists:
        rootScaleDiv = cmds.createNode('multiplyDivide', n = nodename)
        
    
    animNode = 'foot_' + prefix + 'IK_Manual_JNT_translateX'
    cmds.setAttr(rootScaleDiv+'.operation', 2)
    CleanConnectionOnNode(rootScaleDiv, 'input1X', True)
    cmds.connectAttr(totalDistNode+ '.distance', rootScaleDiv + '.input1X')
    CleanConnectionOnNode(rootScaleDiv, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', rootScaleDiv + '.input2X')
    CleanConnectionOnNode(rootScaleDiv, 'outputX', False)
    CleanConnectionOnNode(animNode, 'input', True)
    cmds.connectAttr(rootScaleDiv+'.outputX', animNode + '.input')

    ########## ---------------------------------- ##################
    # Knee Snap
    # distance from knee to thigh
    manualLoc = prefix+"KneeIKManual_LOC"
    manualCtrl = legCTRL[prefix+'KneeIKManual']
    distanceDir = legStat[prefix+'legXDir']
    attrName = 'knee_snap'
    exists = CheckAttributeExists(manualCtrl, attrName)
    if not exists:
        cmds.addAttr(manualCtrl, longName = attrName, niceName = 'Manual Knee Snap', at = 'float', min = 0, max = 1, dv = 0, k = True)

    distName = prefix+"legKneeToThighLengthShape"
    exists, thighDistNode = CheckObjExists(distName)
    if not exists:
        thighDistNode = cmds.createNode('distanceDimShape', n = distName)     
    p1 = manualLoc
    p2 = ThighLocShape
    CleanConnectionOnNode(thighDistNode, 'startPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', thighDistNode + '.startPoint')
    CleanConnectionOnNode(thighDistNode, 'endPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', thighDistNode + '.endPoint')
    pnode = cmds.listRelatives(thighDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, prefix+"legKneeToThighLength", ignoreShape = True)
    lengthNodes.append(prefix+"legKneeToThighLength")
    
    
    # distance from knee to foot
    distName = prefix+"legKneeToFootLengthShape"
    exists, footDistNode = CheckObjExists(distName)
    if not exists:
        footDistNode = cmds.createNode('distanceDimShape', n = distName)     
    p1 = manualLoc
    p2 = FootLocShape
    CleanConnectionOnNode(footDistNode, 'startPoint', True)
    cmds.connectAttr(p1+'.worldPosition[0]', footDistNode + '.startPoint')
    CleanConnectionOnNode(footDistNode, 'endPoint', True)
    cmds.connectAttr(p2+'.worldPosition[0]', footDistNode + '.endPoint')
    pnode = cmds.listRelatives(footDistNode, p = True)[0]
    cmds.setAttr(pnode+'.visibility', False)
    cmds.rename(pnode, prefix+"legKneeToFootLength", ignoreShape = True)
    lengthNodes.append(prefix+"legKneeToFootLength")
    
    
    divName = 'knee_'+prefix+'ThighRootscaleDiv'
    exists,divNode = CheckObjExists(divName)
    if not exists:
        divNode = cmds.createNode('multiplyDivide', n = divName)
    cmds.setAttr(divNode+'.operation', 2)
    CleanConnectionOnNode(divNode, 'input1X', True)
    cmds.connectAttr(thighDistNode+'.distance', divNode+'.input1X')
    CleanConnectionOnNode(divNode, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', divNode+'.input2X')

    mulName = 'knee_'+prefix+'ThighDirX'
    exists,mulNode = CheckObjExists(mulName)
    if not exists:
        mulNode = cmds.createNode('multiplyDivide', n = mulName)
    cmds.setAttr(mulNode+'.operation', 1)
    CleanConnectionOnNode(divNode, 'outputX', False)
    CleanConnectionOnNode(mulNode, 'input1X', True)
    cmds.connectAttr(divNode+'.outputX', mulNode+'.input1X')
    CleanConnectionOnNode(mulNode, 'input2X', True)
    cmds.setAttr(mulNode+'.input2X', distanceDir)

    animNode = 'calf_' + prefix + 'IK_Manual_JNT_translateX'
    nodeName = prefix+"thighKneeManualSnap_Choice"
    exists,blendNode = CheckObjExists(nodeName)
    if not exists:
        blendNode = cmds.createNode('blendColors', n = nodeName)
    CleanConnectionOnNode(mulNode, 'outputX', False)
    CleanConnectionOnNode(blendNode, 'blender', True)
    cmds.connectAttr(manualCtrl+ '.knee_snap', blendNode + '.blender')
    CleanConnectionOnNode(blendNode, 'color1R', True)
    cmds.connectAttr(mulNode+'.outputX', blendNode + '.color1R')
    CleanConnectionOnNode(blendNode, 'color2R', True)
    cmds.connectAttr(animNode+'.output', blendNode + '.color2R')

    # Manual ik leg stretch toggle 
    bname = prefix+'leg_IKManualThighStretchChoice'
    snapChoice = prefix+"thighKneeManualSnap_Choice"
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(snapChoice+'.outputR', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', legStat[prefix+'calfTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)

    
    CleanConnectionOnNode(legIKJNT[prefix+'CalfManual'], 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', legIKJNT[prefix+'CalfManual'] + '.translateX')
    
    
    divName = 'knee_'+prefix+'FootRootscaleDiv'
    exists,divNode = CheckObjExists(divName)
    if not exists:
        divNode = cmds.createNode('multiplyDivide', n = divName)
    cmds.setAttr(divNode+'.operation', 2)
    CleanConnectionOnNode(divNode, 'input1X', True)
    cmds.connectAttr(footDistNode+'.distance', divNode+'.input1X')
    CleanConnectionOnNode(divNode, 'input2X', True)
    cmds.connectAttr(centralCTRL['rootCtrl']+'.scaleX', divNode+'.input2X')
    
    
    mulName = 'knee_'+prefix+'FootDirX'
    exists,mulNode = CheckObjExists(mulName)
    if not exists:
        mulNode = cmds.createNode('multiplyDivide', n = mulName)
    cmds.setAttr(mulNode+'.operation', 1)
    CleanConnectionOnNode(divNode, 'outputX', False)
    CleanConnectionOnNode(mulNode, 'input1X', True)
    cmds.connectAttr(divNode+'.outputX', mulNode+'.input1X')
    CleanConnectionOnNode(mulNode, 'input2X', True)
    cmds.setAttr(mulNode+'.input2X', distanceDir)  

    animNode = 'foot_' + prefix + 'IK_Manual_JNT_translateX'
    nodeName = prefix+"calfKneeManualAuto_Choice"
    exists,blendNode = CheckObjExists(nodeName)
    if not exists:
        blendNode = cmds.createNode('blendColors', n = nodeName)
    CleanConnectionOnNode(mulNode, 'outputX', False)
    CleanConnectionOnNode(blendNode, 'blender', True)
    cmds.connectAttr(manualCtrl+ '.knee_snap', blendNode + '.blender')
    CleanConnectionOnNode(blendNode, 'color1R', True)
    cmds.connectAttr(mulNode+'.outputX', blendNode + '.color1R')
    CleanConnectionOnNode(blendNode, 'color2R', True)
    cmds.connectAttr(animNode+'.output', blendNode + '.color2R')


    bname = prefix+'leg_IKManualCalfStretchChoice'
    snapChoice = prefix+"calfKneeManualAuto_Choice"
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(switchCtrl+'.stretch_toggle', bnode+'.blender')
    CleanConnectionOnNode(bnode, 'color1R', True)
    cmds.connectAttr(snapChoice+'.outputR', bnode+'.color1R')
    cmds.setAttr(bnode+'.color2R', legStat[prefix+'footTranslateX'])
    CleanConnectionOnNode(bnode, 'outputR', False)


    CleanConnectionOnNode(legIKJNT[prefix+'FootManual'], 'translateX', True)
    cmds.connectAttr(bnode+'.outputR', legIKJNT[prefix+'FootManual']+ '.translateX')


    # cleanup grps 
    grpname = legGRP[prefix+'IKConstGRP']
    for ln in lengthNodes:
        AddToGroup(grpname, ln)

    ConfigureFoot(isRight)


    return 1

def ConfigureFoot(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'

    print('## Start foot setup')
    IKCtrl = legCTRL[prefix+'FootIK']
    ballHDL = legHDL[prefix+'Ball']
    toeHDL = legHDL[prefix+'Toe']

    ## setup ik hdl for ball and  toe 
    startjnt = legIKJNT[prefix+'Foot']
    endjnt = legIKJNT[prefix+'Ball']
    hdlname = ballHDL
    exists, balllHDL = CheckObjExists(hdlname)
    if not exists:
        ballHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikSCsolver', sticky ='sticky')[0]
    AddToGroup(IKCtrl, ballHDL)

    startjnt = legIKJNT[prefix+'Ball']
    endjnt = legIKJNT[prefix+'Toe']
    hdlname = toeHDL
    exists, toeHDL = CheckObjExists(hdlname)
    if not exists:
        toeHDL = cmds.ikHandle(name = hdlname, startJoint = startjnt, endEffector = endjnt, solver = 'ikSCsolver', sticky = 'sticky')[0]
    AddToGroup(IKCtrl, toeHDL)
    # Addtional Locators --> Need a way to edit the locators without the impacting the rig:
    locList = ['ball', 'toe', 'heel', 'foot_outer', 'foot_inner']
    grp = IKCtrl
    for loc in locList:
        locname = '{0}_{1}LOC'.format(loc, prefix)
        exists, locnode = CheckObjExists(locname)
        if not exists:
            locnode = cmds.spaceLocator(n = locname, a = True)
        else:
            print("{} Locator exists in the scene, skip creation".format(locname))

        if prefix+loc.title() in legIKJNT:
            print("Snap joint {} to joint".format(loc))
            jntpos = getWSTranslate(legIKJNT[prefix+loc.title()])
            cmds.xform(locnode, t = jntpos, ws = True)

        AddToGroup(IKCtrl, locnode)

    # parent under ball loc 
    ballLocGRP = []
    ballLoc = '{0}_{1}LOC'.format('ball', prefix)
    footHDLGRP = legGRP[prefix+'footHDL']
    ballLocGRP.append(footHDLGRP)
    ballLocGRP.append(ballHDL)
    ballLocGRP.append(legCTRL[prefix+'KneeIKAuto'])
    for c in ballLocGRP:
        AddToGroup(ballLoc, c)

    # parent under toe wiggle grp
    grpname = 'toe_Wiggle_'+prefix+'GRP'
    exists, toeWiggleGRP = CheckObjExists(grpname)
    if not exists:
        toeWiggleGRP = cmds.group(name = grpname, em = True, w = True)
    else:
        RemoveFromGroup(toeWiggleGRP, toeHDL)
    position = getWSTranslate(legIKJNT[prefix+'Ball'])
    cmds.xform(toeWiggleGRP, t = position, ws = True)
    AddToGroup(toeWiggleGRP, toeHDL)

    # parent under foot inner loc 
    footInnerLoc = '{0}_{1}LOC'.format('foot_inner', prefix)
    AddToGroup(footInnerLoc, ballLoc)
    AddToGroup(footInnerLoc, toeWiggleGRP)

    # parent under foot outer loc
    footOuterLoc = '{0}_{1}LOC'.format('foot_outer', prefix)
    AddToGroup(footOuterLoc, footInnerLoc)

    # parent under heel loc 
    heelLoc = '{0}_{1}LOC'.format('heel', prefix)
    AddToGroup(heelLoc, footOuterLoc)

    # parent under toe loc
    toeLoc = '{0}_{1}LOC'.format('toe', prefix)
    AddToGroup(toeLoc, heelLoc)

    # parent toe loc under 'FootLoc_GRP'
    grpname = legGRP[prefix+'FootLocGRP']
    exists, grp = CheckObjExists(grpname)
    if not exists:
        grp = cmds.group(name = grpname, parent = legCTRL[prefix+'FootIK'], em = True)
    
    cmds.xform(grp, t = getWRPivot(legCTRL[prefix+'FootIK']), ws = True)
    AddToGroup(grp, toeLoc)

    ## Set up foot Roll 
    # attribute preparation 
    roll = 'roll'
    exists = CheckAttributeExists(IKCtrl, roll)
    if not exists:
        cmds.addAttr(IKCtrl, longName = roll, niceName = 'Roll', k = True, at = 'float', dv = 0)
    
    toeLiftLimit = 'toe_lift_limit'
    exists = CheckAttributeExists(IKCtrl, toeLiftLimit)
    if not exists:
        cmds.addAttr(IKCtrl, longName = toeLiftLimit, niceName = 'Toe Lift Limit', k = True, at = 'float', dv = 30)

    toeStraitLimit = 'toe_straight_limit'
    exists = CheckAttributeExists(IKCtrl, toeStraitLimit)
    if not exists:
        cmds.addAttr(IKCtrl, longName = toeStraitLimit, niceName = 'Toe Straight Limit', k = True, at = 'float', dv = 0)
    
    # Connect roll with heel rotateX: +X, heel bend down; -X, heel bend up
    benduplimit = -35 # TODO: this value should be exposed to the user 
    clampname = prefix+'HeelRot_Clamp'
    exists, clampnode = CheckObjExists(clampname)
    if not exists:
        clampnode = cmds.createNode('clamp', name = clampname)

    cmds.setAttr(clampnode+'.minR', benduplimit)
    cmds.setAttr(clampnode+'.maxR', 0.0)
    CleanConnectionOnNode(clampnode, 'inputR', True)
    cmds.connectAttr(IKCtrl+'.'+roll, clampnode + '.inputR')
    CleanConnectionOnNode(clampnode, 'outputR', False)
    CleanConnectionOnNode(heelLoc, 'rotateX', True)
    cmds.connectAttr(clampnode+'.outputR', heelLoc+'.rotateX')

    # Connect roll with toe rotateX 
    # toe lift limit: if roll exceeds the limit, toe rotateX ++
    # toe straight limit: if roll exceeds the limit, toe rotate stop increasing, i.e. the foot is without any joint bending 
    clampname = prefix+'ToeBendToStraight_Clamp'
    exists, clampnode = CheckObjExists(clampname)
    if not exists:
        clampnode = cmds.createNode('clamp', name = clampname)
    
    CleanConnectionOnNode(clampnode, 'minR', True)
    cmds.connectAttr(IKCtrl+'.'+toeLiftLimit, clampnode + '.minR')
    CleanConnectionOnNode(clampnode, 'maxR', True)
    cmds.connectAttr(IKCtrl+'.'+toeStraitLimit, clampnode + '.maxR')
    CleanConnectionOnNode(clampnode, 'inputR', True)
    cmds.connectAttr(IKCtrl+'.'+roll, clampnode + '.inputR')
    CleanConnectionOnNode(clampnode, 'outputR', False)
    # connect ouput to range node  

    # remap to 0-1
    rangename = prefix+'ToeBendToStraightPercent_SetRange'
    exists, rangenode = CheckObjExists(rangename)
    if not exists:
        rangenode = cmds.createNode('setRange', name = rangename)

    cmds.setAttr(rangenode + '.minX', 0)
    cmds.setAttr(rangenode + '.maxX', 1)
    CleanConnectionOnNode(rangenode, 'valueX', True)
    cmds.connectAttr(clampnode+'.outputR', rangenode+'.valueX')
    CleanConnectionOnNode(rangenode, 'oldMaxX', True)
    cmds.connectAttr(clampnode+'.maxR', rangenode+'.oldMaxX')
    CleanConnectionOnNode(rangenode, 'oldMinX', True)
    cmds.connectAttr(clampnode+'.minR', rangenode+'.oldMinX')
    CleanConnectionOnNode(rangenode, 'outValueX', False)
    # connect output to multiply node 

    # multiply the 0-1 percentage with roll value to rechieve the rot angle value 
    mulname = prefix+'ToePercentToRot_Multiply'
    exists, mulnode = CheckObjExists(mulname)
    if not exists:
        mulnode = cmds.createNode('multiplyDivide', name = mulname)
    print(mulnode)
    cmds.setAttr(mulnode+'.operation', 1)
    CleanConnectionOnNode(mulnode, 'input1X', True)
    cmds.connectAttr(clampname+'.inputR', mulnode+'.input1X')
    CleanConnectionOnNode(mulnode, 'input2X', True)
    cmds.connectAttr(rangenode+'.outValueX', mulnode+'.input2X')
    CleanConnectionOnNode(mulnode, 'outputX', False)
    # connect output to toeloc rotateX
    CleanConnectionOnNode(toeLoc, 'rotateX', True)
    cmds.connectAttr(mulnode+'.outputX', toeLoc+'.rotateX')

    # Connect roll to ball rotateX
    # when roll is 0 ~ toeliftlimit: ball rot ++
    # when roll is toeliftlimit ~ toestraightlimit: ball rot --, so that the foot would straighten
    clampname = prefix +'BallRot_Clamp'
    exists, clampnode = CheckObjExists(clampname)
    if not exists:
        clampnode = cmds.createNode('clamp', name = clampname)
    
    cmds.setAttr(clampnode + '.minR', 0.0)
    CleanConnectionOnNode(clampnode, 'maxR', True)
    cmds.connectAttr(IKCtrl+'.'+toeLiftLimit, clampnode + '.maxR')
    CleanConnectionOnNode(clampnode, 'inputR', True)
    cmds.connectAttr(IKCtrl+'.'+roll, clampnode + '.inputR')
    CleanConnectionOnNode(clampnode, 'outputR', False)
    # connect to setrange node 

    # remap to 0-1
    rangename = prefix+'BallRotPercent_SetRange'
    exists, rangenode = CheckObjExists(rangename)
    if not exists:
        rangenode = cmds.createNode('setRange', name = rangename)

    cmds.setAttr(rangenode + '.minX', 0)
    cmds.setAttr(rangenode + '.maxX', 1)
    CleanConnectionOnNode(rangenode, 'valueX', True)
    cmds.connectAttr(clampnode+'.outputR', rangenode+'.valueX')
    CleanConnectionOnNode(rangenode, 'oldMaxX', True)
    cmds.connectAttr(clampnode+'.maxR', rangenode+'.oldMaxX')
    CleanConnectionOnNode(rangenode, 'oldMinX', True)
    cmds.connectAttr(clampnode+'.minR', rangenode+'.oldMinX')
    CleanConnectionOnNode(rangenode, 'outValueX', False)


    minusname = prefix+'BallOneMinusPercent_Minus'
    toepercentnode = prefix+'ToeBendToStraightPercent_SetRange'
    exists, minusnode = CheckObjExists(minusname)
    if not exists: 
        minusnode = cmds.createNode('plusMinusAverage', name = minusname)
    
    # set operation to subtract
    cmds.setAttr(minusnode+'.operation', 2) 
    #CleanConnectionOnNode(minusnode, 'input1D[0]', True)
    #cmds.connectAttr(toepercentnode+'.outValueX', minusnode + '.input1D[0]')
    #CleanConnectionOnNode(minusnode, 'input1D[0]', True)
    cmds.setAttr(minusnode+'.input1D[0]', 1)
    CleanConnectionOnNode(minusnode, 'input1D[1]', True)
    cmds.connectAttr(toepercentnode+'.outValueX', minusnode + '.input1D[1]')
    CleanConnectionOnNode(minusnode, 'output1D', False)
    # output to final percent mul

    mulname = prefix+'BallFinalPercent_Multiply'
    exists, mulnode = CheckObjExists(mulname)
    print (exists)
    if not exists:
        mulnode = cmds.createNode('multiplyDivide', name = mulname)
    print(mulnode)
    cmds.setAttr(mulnode+'.operation', 1)
    CleanConnectionOnNode(mulnode, 'input1X', True)
    cmds.connectAttr(minusnode+'.output1D', mulnode+'.input1X')
    CleanConnectionOnNode(mulnode, 'input2X', True)
    cmds.connectAttr(rangenode+'.outValueX', mulnode+'.input2X')
    CleanConnectionOnNode(mulnode, 'outputX', False)
    # connect output to percet to rot multiply 

    mulname = prefix+'BallPercentToRot_Multiply'
    finalpercet = prefix+'BallFinalPercent_Multiply'
    rotclamp = prefix +'BallRot_Clamp'
    exists, mulnode = CheckObjExists(mulname)
    if not exists:
        mulnode = cmds.createNode('multiplyDivide', name = mulname)
    print(mulnode)
    cmds.setAttr(mulnode+'.operation', 1)
    CleanConnectionOnNode(mulnode, 'input1X', True)
    cmds.connectAttr(finalpercet+'.outputX', mulnode+'.input1X')
    CleanConnectionOnNode(mulnode, 'input2X', True)
    cmds.connectAttr(rotclamp+'.inputR', mulnode+'.input2X')
    CleanConnectionOnNode(mulnode, 'outputX', False)
    # output to ballloc rotateX
    CleanConnectionOnNode(ballLoc, 'rotateX', True)
    cmds.connectAttr(mulnode+'.outputX', ballLoc+'.rotateX')

    ## Set up tilt 
    attrname = 'tilt'
    rotZDir = 1
    if not isRight:
        rotZDir = -1
    exists = CheckAttributeExists(IKCtrl, attrname)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attrname, niceName = 'Tilt', k = True, dv = 0, at = 'float')
    
    # set driven key with foot_outer_loc, foot_inner_loc 
    # right foot: tilt < 0, tilt inwards, tilt > 0, tilt outwards
    animNode = 'foot_inner_' + prefix + 'LOC_rotateZ'
    exists, node = CheckObjExists(animNode)
    if exists:
        cmds.delete(animNode)
    print ("Create New Curve")
    cmds.setDrivenKeyframe(footInnerLoc, attribute='rotateZ', currentDriver = IKCtrl+'.tilt', driverValue = 0, value = 0) 
    cmds.setDrivenKeyframe(footInnerLoc, attribute='rotateZ', currentDriver = IKCtrl+'.tilt', driverValue = -90, value = -90*rotZDir)
    cmds.keyTangent(footInnerLoc, attribute='rotateZ', itt = 'spline', ott = 'spline')

    animNode = 'foot_outer_' + prefix + 'LOC_rotateZ'
    exists, node = CheckObjExists(animNode)
    if exists:
        cmds.delete(animNode)
    print ("Create New Curve")
    cmds.setDrivenKeyframe(footOuterLoc, attribute='rotateZ', currentDriver = IKCtrl+'.tilt', driverValue = 0, value = 0) 
    cmds.setDrivenKeyframe(footOuterLoc, attribute='rotateZ', currentDriver = IKCtrl+'.tilt', driverValue = 90, value = 90*rotZDir)
    cmds.keyTangent(footOuterLoc, attribute='rotateZ', itt = 'spline', ott = 'spline')


    ## Set up lean 
    attrname = 'lean'
    exists = CheckAttributeExists(IKCtrl, attrname)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attrname, niceName = 'Lean', k = True, dv = 0, at = 'float')
    CleanConnectionOnNode(ballLoc, 'rotateZ', True)
    cmds.connectAttr(IKCtrl+'.'+attrname, ballLoc+'.rotateZ')

    ## Set up toe spin 
    attrname = 'toe_spin'
    exists = CheckAttributeExists(IKCtrl, attrname)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attrname, niceName = 'Toe Spin', k = True, dv = 0, at = 'float')
    CleanConnectionOnNode(toeLoc, 'rotateY', True)
    cmds.connectAttr(IKCtrl+'.'+attrname, toeLoc+'.rotateY')

    ## Set up toe wiggle 
    attrname = 'toe_wiggle'
    exists = CheckAttributeExists(IKCtrl, attrname)
    if not exists:
        cmds.addAttr(IKCtrl, longName = attrname, niceName = 'Toe Spin', k = True, dv = 0, at = 'float')
    CleanConnectionOnNode(toeWiggleGRP, 'rotateX', True)
    cmds.connectAttr(IKCtrl+'.'+attrname, toeWiggleGRP+'.rotateX')

    return 1

def ConnectLegToTorso(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'

    ## code stats here 
    # GRP everything with leg under the rig grp 
    grpname = legGRP[prefix+'RigGRP']
    exists, rigGRP = CheckObjExists(grpname)
    if not exists:
        rigGRP = cmds.group(name = grpname, parent = centralCTRL['rootCtrl'], em = True)
    
    grpchildren = []
    # add all measure nodes to the riggrp
    measureLength = cmds.ls('{prefix}*Length'.format(prefix = prefix+'leg'))
    print (measureLength)
    grpchildren += measureLength
    jointGRP = cmds.ls('leg_{prefix}*Const_GRP'.format(prefix = prefix))
    print (jointGRP)
    grpchildren += jointGRP
    grpchildren += cmds.ls(legCTRL[prefix+'FootIK'])
    grpchildren += cmds.ls(legCTRL[prefix+'KneeIKManual'])

    for gc in grpchildren:
        AddToGroup(rigGRP, gc)


    # pivot for all leg grps 
    legpivot = legResultJNT[prefix+'Thigh']
    
    # create locator for leg translation, and fix it in the pelvisSpace group 
    locname = prefix+'leg_Translate_LOC'
    spaceGRP = partSpaceGRP['pelvis']
    exists, locNode = CheckObjExists(locname)
    if exists:
        cmds.delete(locNode)
    locNode = cmds.spaceLocator(n = locname, p = getWSTranslate(legpivot), r = True) 
    cmds.xform(locNode, centerPivots = True)
        
    AddToGroup(spaceGRP, locNode)
    cmds.setAttr(locNode[0]+'.visibility', 0)
    
    
    orientTargets = []
    
    # create locators for leg orientation shoulderSpace, bodySpace, rootSpace
    locindex = ['pelvis', 'body', 'root']
    for l in locindex:
        locname = prefix+'leg_'+l+'SpaceRotate_LOC'
        spaceGRP = partSpaceGRP[l]
        exists, locNode = CheckObjExists(locname)
        if exists:
            cmds.delete(locNode)
        locNode = cmds.spaceLocator(n = locname, p = getWSTranslate(legpivot), a = True) 
        cmds.xform(locNode, centerPivots = True)          
        AddToGroup(spaceGRP, locNode)
        cmds.setAttr(locNode[0]+'.visibility', 0)
        orientTargets.append(locNode[0])
    
    
    # point IKConst_GRP, FKConst_GRP, resultConst_GRP with tanslate_LOC
    grplist = [legGRP[prefix+'IKConstGRP'], legGRP[prefix+'FKConstGRP'], legGRP[prefix+'ResultConstGRP']]
    for grp in grplist:
        constraint = cmds.pointConstraint(prefix+'leg_Translate_LOC', grp, name = prefix+grp+'_FollowPointConstraint')
    
    
    # create leg follow attr on the fk upperleg ctrl 
    objname = legCTRL[prefix+'ThighFK']
    attrname = 'orient_follow_space'
    exists = CheckAttributeExists(objname, attrname)
    if not exists:
        cmds.addAttr(objname, longName = attrname, niceName = 'Orient Follow Space', attributeType = 'enum', enumName = 'Pelvis:Upperbody:Root', k = True)   
    
    # orient FKConst_GRP, resultConst_GRP with shoulderSpace, bodySpace and RootSpace
    grp = legGRP[prefix+'FKConstGRP']
    constraint = cmds.orientConstraint(orientTargets, grp, name = prefix+grp+'_FollowOrientConstraint')[0]
    index = 0
    for loc in orientTargets: 
        attr = '{0}W{1}'.format(loc,index)
        cmds.delete(constraint, at = attr, e = True)
        expname = grp+'_'+attr+'_OrientExpression'
        exists, exp = CheckObjExists(expname)
        if exists:
            print("##delete current exp {}".format(exp))
            cmds.delete(exp)
        
        expstring = "if({targetAttr} == {index}){{{constraint}.{at} = 1;}}else{{{constraint}.{at} = 0;}}".format(targetAttr = objname+'.'+attrname, constraint = constraint, at = attr, index = index)
        index = index + 1
        #print(expstring)
        cmds.expression(o = constraint, s = expstring, ae = True, n = expname) 
        
        
    grp = legGRP[prefix+'ResultConstGRP']
    constraint = cmds.orientConstraint(orientTargets, grp, name = prefix+grp+'_FollowOrientConstraint')[0]
    index = 0
    for loc in orientTargets: 
        attr = '{0}W{1}'.format(loc,index)
        cmds.delete(constraint, at = attr, e = True)
        expname = grp+'_'+attr+'_OrientExpression'
        exists, exp = CheckObjExists(expname)
        if exists:
            print("##delete current exp {}".format(exp))
            cmds.delete(exp)
        
        expstring = "if({targetAttr} == {index}){{{constraint}.{at} = 1;}}else{{{constraint}.{at} = 0;}}".format(targetAttr = objname+'.'+attrname, constraint = constraint, at = attr, index = index)
        index = index + 1
        #print(expstring)
        cmds.expression(o = constraint, s = expstring, ae = True, n = expname) 
    
    CleanConnectionOnNode(legGRP[prefix+'ResultConstGRP'] ,'rotate',True)
    CleanConnectionOnNode(legGRP[prefix+'ResultConstGRP'] ,'rotateX',True)
    CleanConnectionOnNode(legGRP[prefix+'ResultConstGRP'] ,'rotateY',True)
    CleanConnectionOnNode(legGRP[prefix+'ResultConstGRP'] ,'rotateZ',True)

    # Choice for orient ResultConst_GRP: IK follow IKConstGRP, FK follow choice of space?
    bname = prefix+'leg_resultConstGRPOreintChoice'
    exists, bnode = CheckObjExists(bname)
    if not exists:
        bnode = cmds.createNode('blendColors', name = bname)
    
    constraint = prefix+legGRP[prefix+'ResultConstGRP']+'_FollowOrientConstraint'
    IKOrient = legGRP[prefix+'IKConstGRP']
    CleanConnectionOnNode(bnode, 'color1', True)    
    cmds.connectAttr(IKOrient + '.rotate', bnode + '.color1')
    CleanConnectionOnNode(bnode, 'color2', True) 
    cmds.connectAttr(constraint + '.constraintRotate', bnode + '.color2')
    CleanConnectionOnNode(bnode, 'output', False)
    cmds.connectAttr(bnode + '.output', legGRP[prefix+'ResultConstGRP'] + '.rotate')
    CleanConnectionOnNode(bnode, 'blender', True)
    cmds.connectAttr(legCTRL[prefix+'Switch']+'.FKIK_blend', bnode + '.blender')

    return 1

# IK >>> FK
def LegSwitchMatchIK2FK(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
    else:
        prefix = 'l_'

    ## code stats here 
    switchCtrl = legCTRL[prefix+'Switch']
    print("Leg IK >>> FK")
    fkjnt = legFKJNT[prefix+'Thigh']
    snapjnt = legFKJNT[prefix+'Thigh']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

    fkjnt = legFKJNT[prefix+'Calf']
    snapjnt = legFKJNT[prefix+'Calf']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True)

    fkjnt = legFKJNT[prefix+'Foot']
    snapjnt = legFKJNT[prefix+'Foot']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True) 

    fkjnt = legFKJNT[prefix+'Ball']
    snapjnt = legFKJNT[prefix+'Ball']+'SnapTo'
    print(fkjnt)
    cmds.xform(fkjnt, ro = getWSRotate(snapjnt), ws = True) 
    
    # match fk leg lenght to ik 
    manualctrl = legCTRL[prefix+'KneeIKManual']
    kneesnap = cmds.getAttr(manualctrl + '.knee_snap')
    upperStretchRatio = 1
    lowerStretchRatio = 1
    if kneesnap == 0:
        # use the seperate length 
        totaldist = cmds.getAttr(prefix+'legIKTotalLengthShape'+'.distance')
        upperStretchRatio = totaldist / legStat[prefix+'IKtotalLength']
        lowerStretchRatio = totaldist / legStat[prefix+'IKtotalLength']
        if upperStretchRatio < 1:
            upperStretchRatio = 1
        if lowerStretchRatio < 1:
            lowerStretchRatio = 1
    elif kneesnap == 1:
        # use total length 
        upperdist = cmds.getAttr(prefix+'legKneeToThighLengthShape'+'.distance')
        lowerdist = cmds.getAttr(prefix+'legKneeToFootLengthShape'+'.distance')
        upperStretchRatio = upperdist / legStat[prefix+'calfTranslateX'] * legStat[prefix+'legXDir']
        lowerStretchRatio = lowerdist / legStat[prefix+'footTranslateX'] * legStat[prefix+'legXDir']
    else:
        print("knee snap is between 0-1, should we blend the length? ")

    print("## upperleg ratio is {0} ; lowerleg ratio is {1}".format(upperStretchRatio, lowerStretchRatio))
    cmds.setAttr(legCTRL[prefix+'ThighFK'] + '.length' , upperStretchRatio)
    cmds.setAttr(legCTRL[prefix+'CalfFK'] + '.length' , lowerStretchRatio)

    # set to FK mode
    cmds.setAttr(switchCtrl+'.FKIK_blend', 0)

    return 1

def LegAutoTwistMatch(currentJnt, originJntPos, anchorJnt, targetAngle, twistAttr, twistAmount, tolerance, count):
    # set twist 
    cmds.setAttr(twistAttr, twistAmount)
    anchorToCurrent = getVectorMinus(getWSTranslate(currentJnt), getWSTranslate(anchorJnt))
    anchorToOrigin = getVectorMinus(originJntPos, getWSTranslate(anchorJnt))
    currentAngle = cmds.angleBetween(vector1 = anchorToCurrent, vector2 = anchorToOrigin)[3]
    #print(count)
    if count >= 10000:
        print ('[FAILED] Auto twist matching exceeds maximun iteration, abort!')
        return 0
    else:
        #print(currentAngle)
        if abs(currentAngle - targetAngle) < tolerance:
            return twistAmount
        else:
            count += 1
            if currentAngle > targetAngle:
                twistAmount = twistAmount - twistAmount/2
            else:
                twistAmount = twistAmount + twistAmount/2
            #print(twistAmount)
            return LegAutoTwistMatch(currentJnt, originJntPos, anchorJnt, targetAngle, twistAttr, twistAmount, tolerance, count)
    

# FK >>> IK
def LegSwitchMatchFK2IK(isRight):
    prefix = ''
    if isRight:
        prefix = 'r_'
        isKneeManual = isMatchingRightKneeManual
    else:
        prefix = 'l_'
        isKneeManual = isMatchingLeftKneeManual

    ## code stats here 
    print("Leg FK >>> IK")
    # matching knee position 
    IKCtrl = legCTRL[prefix+'FootIK']

    if isKneeManual:
        manualctrl = legCTRL[prefix+'KneeIKManual']
        calfjnt = legResultJNT[prefix + 'Calf']
        footsnap = legFKJNT
        newt = getWSTranslate(calfjnt)
        cmds.xform(manualctrl, t = newt, ws = True) 
        cmds.setAttr(IKCtrl+'.manual_auto_blend', 0)
    else:
        cmds.setAttr(IKCtrl+'.manual_auto_blend', 1)
    
    

    # matching foot ctrl position 
    rootctrl = centralCTRL['rootCtrl']
    rootOffset = getWSTranslate(rootctrl)
    
    defaultIKCTRL = legCTRL[prefix+'FootIK']+'Default'
    snapIKCTRL = legCTRL[prefix+'FootIK']+'SnapTo'
    # Matching pivot 
    pivotOffset = getVectorMinus(getWRPivot(snapIKCTRL), getWRPivot(defaultIKCTRL))
    IKTranslate = getVectorAdd(pivotOffset, rootOffset)
    cmds.xform(IKCtrl, t = IKTranslate, ws = True)
    print("[Debug] Before Matching {0} ws rot is {1}, {2} ws rot is {3}".format(IKCtrl, getWSRotate(IKCtrl),
                snapIKCTRL, getWSRotate(snapIKCTRL)))
    snapRotate = getWSRotate(snapIKCTRL)
    cmds.xform(IKCtrl, ro = snapRotate, ws = True)

    print("[Debug] After Matching {0} ws rot is {1}, {2} ws rot is {3}".format(IKCtrl, getWSRotate(IKCtrl),
                snapIKCTRL, getWSRotate(snapIKCTRL)))
    # Matching Length 

    #match manual leg length 
    curUpperlegDist = cmds.getAttr(legFKJNT[prefix + 'Calf']+ '.translateX')
    curLowerlegDist = cmds.getAttr(legFKJNT[prefix + 'Foot']+ '.translateX')
    defaultUpperlegDist = legStat[prefix+'calfTranslateX']
    defaultLowerlegDist = legStat[prefix+'footTranslateX']

    if isKneeManual:
        if abs(curUpperlegDist - defaultUpperlegDist) > 0.002 or abs(curLowerlegDist - defaultLowerlegDist) > 0.002 : 
            # enable manual knee snap 
            cmds.setAttr(manualctrl + '.knee_snap', 1)
            cmds.setAttr(IKCtrl+'.upper_length', 1)
            print ('## FK >>> IK, matching length, enable manual knee snap')
        else:
            cmds.setAttr(manualctrl + '.knee_snap', 0)
            cmds.setAttr(IKCtrl+'.lower_length', 1)
            print ('## FK >>> IK, matching length, enable manual knee snap')
    else:
        uniformRatio = cmds.getAttr(legIKJNT[prefix+'CalfAuto']+'.translateX')/defaultUpperlegDist
        print(uniformRatio)
        upperRatio = curUpperlegDist/(defaultUpperlegDist*uniformRatio)
        lowerRatio = curLowerlegDist/(defaultLowerlegDist*uniformRatio)
        print('Upperratio is {0}, lowerratio is {1}'.format(upperRatio, lowerRatio))

        cmds.setAttr(IKCtrl+'.upper_length', upperRatio)
        cmds.setAttr(IKCtrl+'.lower_length', lowerRatio)
        # matching the twist value 
        twistAttr = IKCtrl + '.knee_twist'
        
        cmds.setAttr(twistAttr, 0)

        currentJnt = legIKJNT[prefix+'CalfAuto']
        targetJnt = legFKJNT[prefix+'Calf']
        # position of the current jnt when in default pos: knee_twist = 0
        originJntPos = []
        originJntPos = getWSTranslate(legIKJNT[prefix+'CalfAuto'])
        anchorJnt = legIKJNT[prefix+'Foot']
        twistAmount = 90.0
        targetToAnchor = getVectorMinus(getWSTranslate(targetJnt), getWSTranslate(anchorJnt))
        originToAnchor = getVectorMinus(originJntPos, getWSTranslate(anchorJnt))
        targetAngle = cmds.angleBetween(vector1 = targetToAnchor, vector2 = originToAnchor)[3]
        print(targetAngle)
        tolerance = 0.01
        count = 0
        print("## Start Auto Knee twist matching!! Please wait ... ")
        finalTwist = LegAutoTwistMatch(currentJnt, originJntPos, anchorJnt, targetAngle, twistAttr, twistAmount, tolerance, count)
        # compare if the targetjnt pos and currentjnt pos
        deltapos = getVectorMinus(getWSTranslate(targetJnt), getWSTranslate(currentJnt))
        if abs(deltapos[0]) > tolerance or abs(deltapos[1]) > tolerance or abs(deltapos[2]) > tolerance: 
            finalTwist = -finalTwist

        print("## Final Twist is : {}".format(finalTwist))
        cmds.setAttr(twistAttr, finalTwist)

    # matching toe wiggle 
    toeWiggleAmount = cmds.getAttr(legCTRL[prefix+'BallFK']+'.rotateY')
    cmds.setAttr(IKCtrl+'.toe_wiggle', toeWiggleAmount)
        

    switchctrl = legCTRL[prefix+'Switch']
    cmds.setAttr(switchctrl + '.FKIK_blend', 1)

    return 1


###################
# main entry for ui 
###################

#CreateContorlCurvesAndParentTo("test", "test", (0,0,1))

def Launch():
    print(cmds.window("mainWindow", exists=True))
    InitJointNames()		
    registerControllerBasedOnNameConvenstion()

    if (cmds.window('mainWindow', exists=True)):
        cmds.deleteUI('mainWindow')

    mainWindow = cmds.window("mainWindow", title="Auto-Rig Setup", widthHeight=(900, 500) )

    
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    # As we add contents to the window, align them vertically
    colSetup = cmds.columnLayout( adjustableColumn=True )
       
    cmds.separator(horizontal = True, parent = colSetup, height = 10)

    cmds.rowLayout(numberOfColumns=5)
    cmds.button( label='Set Up RIGHT Arm FK, IK blend', command='JointIKFKBlendSetup(True, "arm")')
    cmds.button( label='Configure RIGHT Arm Result JNT', command='ConfigureResultJoint(True, "arm")')
    cmds.button( label='Configure RIGHT Arm FK JNT', command='ConfigureFKArm(True)')
    cmds.button( label='Configure RIGHT Arm IK JNT', command='ConfigureIKArm(True)')
    cmds.button( label='Connect RIGHT Arm To Torso', command='ConnectArmToTorso(True)')
    # A button that does nothing

    cmds.setParent(colSetup)

    cmds.separator(horizontal = True, parent = colSetup, height = 10)
    cmds.rowLayout(numberOfColumns=5)
    cmds.button( label='Set Up LEFT Arm FK, IK blend', command='JointIKFKBlendSetup(False, "arm")')
    cmds.button( label='Configure LEFT Arm Result JNT', command='ConfigureResultJoint(False, "arm")')
    cmds.button( label='Configure LEFT Arm FK JNT', command='ConfigureFKArm(False)')
    cmds.button( label='Configure LEFT Arm IK JNT', command='ConfigureIKArm(False)')
    cmds.button( label='Connect LEFT Arm To Torso', command='ConnectArmToTorso(False)')
    # A button that does nothing

    cmds.setParent(colSetup)
    
    cmds.separator(horizontal = True, parent = colSetup, height = 10)
    cmds.rowLayout(numberOfColumns=5)
    cmds.button( label='Set Up LEFT Leg FK, IK blend', command='JointIKFKBlendSetup(False, "leg")')
    cmds.button( label='Configure LEFT Leg Result JNT', command='ConfigureResultJoint(False, "leg")')
    cmds.button( label='Configure LEFT Leg FK JNT', command='ConfigureFKLeg(False)')
    cmds.button( label='Configure LEFT Leg IK JNT', command='ConfigureIKLeg(False)')
    cmds.button( label='Connect LEFT Leg To Torso', command='ConnectLegToTorso(False)')

    cmds.setParent(colSetup)
    
    cmds.separator(horizontal = True, parent = colSetup, height = 10)
    cmds.rowLayout(numberOfColumns=5)
    cmds.button( label='Set Up RIGHT Leg FK, IK blend', command='JointIKFKBlendSetup(True, "leg")')
    cmds.button( label='Configure RIGHT Leg Result JNT', command='ConfigureResultJoint(True, "leg")')
    cmds.button( label='Configure RIGHT Leg FK JNT', command='ConfigureFKLeg(True)')
    cmds.button( label='Configure RIGHT Leg IK JNT', command='ConfigureIKLeg(True)')
    cmds.button( label='Connect RIGHT Leg To Torso', command='ConnectLegToTorso(True)')
    # A button that does nothing

    cmds.setParent(colSetup)

    cmds.separator(horizontal = True, parent = colSetup, height = 20)
    # FKIK arm switch and match 
    

    # tab for rig set up 
    
    cmds.setParent('..')  
    
    #cmds.rowLayout(numberOfColumns=2)
    # Close button with a command to delete the UI
    #cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
    # Set its parent to the Maya window (denoted by '..')
    
    # Show the window that we created (window)
    #cmds.tabLayout(tabs, tl = ((colSetup,'Setup Tab')))

    colAnimate = cmds.rowColumnLayout()

    cmds.rowLayout(numberOfColumns=3)
    cmds.button( label='LEFT Arm switch IK >>> FK', command='ArmMatchFK2IK(False)')
    cmds.button( label='LEFT Arm switch FK >>> IK', command='ArmMatchIK2FK(False)')
    cmds.columnLayout(adjustableColumn=True )
    cmds.radioCollection()
    cmds.radioButton( label = 'IK Forearm', sl = True, onCommand='setElbowForearmMatching(False, False)')
    cmds.radioButton( label = 'FK Forearm', sl = False, onCommand='setElbowForearmMatching(False, True)')
    cmds.setParent(colAnimate)

    cmds.rowLayout(numberOfColumns=3)
    cmds.button( label='RIGHT Arm switch IK >>> FK', command='ArmMatchFK2IK(True)')
    cmds.button( label='RIGHT Arm switch FK >>> IK', command='ArmMatchIK2FK(True)')
    cmds.columnLayout(adjustableColumn=True )
    cmds.radioCollection()
    cmds.radioButton( label = 'IK Forearm', sl = True, onCommand='setElbowForearmMatching(True, False)')
    cmds.radioButton( label = 'FK Forearm', sl = False, onCommand='setElbowForearmMatching(True, True)')
    cmds.setParent(colAnimate)

    cmds.separator(horizontal = True, parent = colAnimate, height = 20)
    # FKIK leg switch and match 
    cmds.rowLayout(numberOfColumns=3)
    cmds.button( label='LEFT LEG switch IK >>> FK', command='LegSwitchMatchIK2FK(False)')
    cmds.button( label='LEFT LEG switch FK >>> IK', command='LegSwitchMatchFK2IK(False)')
    cmds.columnLayout(adjustableColumn=True )
    cmds.radioCollection()
    cmds.radioButton( label = 'Manual Knee', sl = True, onCommand='setKneeManualMatching(False, True)')
    cmds.radioButton( label = 'Auto Knee', sl = False, onCommand='setKneeManualMatching(False, False)')
    cmds.setParent(colAnimate)

    cmds.rowLayout(numberOfColumns=3)
    cmds.button( label='RIGHT LEG switch IK >>> FK', command='LegSwitchMatchIK2FK(True)')
    cmds.button( label='RIGHT LEG switch FK >>> IK', command='LegSwitchMatchFK2IK(True)')
    cmds.columnLayout(adjustableColumn=True )
    cmds.radioCollection()
    cmds.radioButton( label = 'Manual Knee', sl = True, onCommand='setKneeManualMatching(True, True)')
    cmds.radioButton( label = 'Auto Knee', sl = False, onCommand='setKneeManualMatching(True, False)')
    cmds.setParent(colAnimate)

    

    cmds.rowLayout(numberOfColumns=3)
    cmds.radioCollection()
    cmds.columnLayout(width = 200)
    cmds.text( label = 'Torso Stretch')
    cmds.radioButton( label = 'Enable', sl = True, onCommand='setTorsoStretching(True)')
    cmds.radioButton( label = 'Disable', sl = False, onCommand='setTorsoStretching(False)')
    cmds.setParent('..')
    cmds.radioCollection()
    cmds.columnLayout(width = 200)
    cmds.text( label = 'Arm Stretch')
    cmds.radioButton( label = 'Enable', sl = True, onCommand='setArmStretching(True)')
    cmds.radioButton( label = 'Disable', sl = False, onCommand='setArmStretching(False)')
    cmds.setParent('..')
    cmds.radioCollection()
    cmds.columnLayout(width = 200)
    cmds.text( label = 'Leg Stretch')
    cmds.radioButton( label = 'Enable', sl = True, onCommand='setLegStretching(True)')
    cmds.radioButton( label = 'Disable', sl = False, onCommand='setLegStretching(False)')
    cmds.setParent('..')
    cmds.setParent(colAnimate)

    cmds.rowLayout(numberOfColumns=3)
    cmds.button( label='KEY ALL',  width = 300, height = 50, command='keyAllCtrl()')
    cmds.button( label='Select ALL',  width = 300, height = 50, command='selectAllCtrl()')
    cmds.setParent(colAnimate)

    cmds.setParent( '..' )


    cmds.tabLayout( tabs, edit=True, tabLabel=((colSetup, 'Setup'),(colAnimate, 'Animate')) )

    return mainWindow




