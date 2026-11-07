local N={}
local function idx(n) N[getName(n)]=n; for i=0,getNumOfChildren(n)-1 do idx(getChildAt(n,i)) end end
idx(getRootNode())
if N["chassis8x4"] then setVisibility(N["chassis8x4"],true) end
if N["chassis8x4_tag"] then setVisibility(N["chassis8x4_tag"],true) end
if N["steeringCenterNode"] then setTranslation(N["steeringCenterNode"],0,0,-1.426) end
if N["backlights"] then setTranslation(N["backlights"],0,0,-2.702) end
if N["licensePlateBack"] then setTranslation(N["licensePlateBack"],0.925,0.909,-4.113) end
if N["mudflaps"] then setTranslation(N["mudflaps"],0,0,-2.702) end
if N["trailerAttacherJointSemi"] then setTranslation(N["trailerAttacherJointSemi"],0,1.508,-2.944) end
if N["outdoorCameraTarget"] then setTranslation(N["outdoorCameraTarget"],0,2.26,-0.03) end
if N["roofGlobetrotterXL"] then setVisibility(N["roofGlobetrotterXL"],false) end
if N["roofGlobetrotterXLPart_fh16"] then setVisibility(N["roofGlobetrotterXLPart_fh16"],false) end
if N["roofGlobetrotterXLPart_fhElectric"] then setVisibility(N["roofGlobetrotterXLPart_fhElectric"],false) end
if N["roofGlobetrotterXL_fhElectric_decals"] then setVisibility(N["roofGlobetrotterXL_fhElectric_decals"],false) end
if N["roofSleeper"] then setVisibility(N["roofSleeper"],true) end
if N["roofSleeperPart_fh16"] then setVisibility(N["roofSleeperPart_fh16"],true) end
if N["roofSleeperPart_fhElectric"] then setVisibility(N["roofSleeperPart_fhElectric"],true) end
if N["sidePlanks_fh16"] then setVisibility(N["sidePlanks_fh16"],false) end
if N["brandLogo_decals"] then setVisibility(N["brandLogo_decals"],true) end
if N["aeroPartsCabin"] then setVisibility(N["aeroPartsCabin"],false) end
if N["aeroPartsGlobetrotterXL"] then setVisibility(N["aeroPartsGlobetrotterXL"],false) end
if N["aeroPartsSleeper"] then setVisibility(N["aeroPartsSleeper"],false) end
if N["roofSleeperPart_fhElectric"] then setVisibility(N["roofSleeperPart_fhElectric"],false) end
if N["roofGlobetrotterXLPart_fhElectric"] then setVisibility(N["roofGlobetrotterXLPart_fhElectric"],false) end
if N["switchLightBullbarYes"] then setVisibility(N["switchLightBullbarYes"],false) end
if N["switchLightBullbarNo"] then setVisibility(N["switchLightBullbarNo"],true) end
if N["bullbar01"] then setVisibility(N["bullbar01"],false) end
if N["bullbar02"] then setVisibility(N["bullbar02"],false) end
if N["bullbar03"] then setVisibility(N["bullbar03"],false) end
if N["topBar"] then setVisibility(N["topBar"],false) end
if N["topBarBeaconMount"] then setVisibility(N["topBarBeaconMount"],false) end
if N["topBarLights"] then setVisibility(N["topBarLights"],false) end
if N["airHornMount"] then setVisibility(N["airHornMount"],false) end
if N["switchBeaconYes"] then setVisibility(N["switchBeaconYes"],false) end
if N["switchBeaconNo"] then setVisibility(N["switchBeaconNo"],true) end
if N["beaconYes_decals"] then setVisibility(N["beaconYes_decals"],false) end
if N["switchLighttopBarYes"] then setVisibility(N["switchLighttopBarYes"],false) end
if N["switchLighttopBarNo"] then setVisibility(N["switchLighttopBarNo"],true) end
if N["mudflapsWarning"] then setVisibility(N["mudflapsWarning"],false) end
if N["mudflapsVolvo_decals"] then setVisibility(N["mudflapsVolvo_decals"],true) end
if N["additionalMirror01"] then setVisibility(N["additionalMirror01"],true) end
if N["additionalMirror02"] then setVisibility(N["additionalMirror02"],true) end
if N["safetyGrid"] then setVisibility(N["safetyGrid"],false) end
if N["curtainLeftProEdition"] then setVisibility(N["curtainLeftProEdition"],false) end
if N["curtainRightProEdition"] then setVisibility(N["curtainRightProEdition"],false) end
if N["doorLeftProEdition"] then setVisibility(N["doorLeftProEdition"],false) end
if N["doorRightProEdition"] then setVisibility(N["doorRightProEdition"],false) end
if N["curtainLeftDesignKrone"] then setVisibility(N["curtainLeftDesignKrone"],false) end
if N["curtainRightDesignKrone"] then setVisibility(N["curtainRightDesignKrone"],false) end
if N["curtainLeftDesignFSL"] then setVisibility(N["curtainLeftDesignFSL"],false) end
if N["curtainRightDesignFSL"] then setVisibility(N["curtainRightDesignFSL"],false) end
if N["curtainLeftDesignGIANTS"] then setVisibility(N["curtainLeftDesignGIANTS"],false) end
if N["curtainRightDesignGIANTS"] then setVisibility(N["curtainRightDesignGIANTS"],false) end
if N["fh16_globetrotter_decals"] then setVisibility(N["fh16_globetrotter_decals"],true) end
if N["engine425_decals"] then setVisibility(N["engine425_decals"],true) end
if N["engine515_decals"] then setVisibility(N["engine515_decals"],false) end
if N["engine585_decals"] then setVisibility(N["engine585_decals"],false) end
if N["engine600_decals"] then setVisibility(N["engine600_decals"],false) end
if N["engine700_decals"] then setVisibility(N["engine700_decals"],false) end
if N["engine780_decals"] then setVisibility(N["engine780_decals"],false) end
if N["fh16_780_decals"] then setVisibility(N["fh16_780_decals"],false) end
if N["cabin_fh16"] then setVisibility(N["cabin_fh16"],true) end
if N["cabin_fhElectric"] then setVisibility(N["cabin_fhElectric"],false) end
if N["chassisMain_fh16"] then setVisibility(N["chassisMain_fh16"],true) end
if N["chassisMain_fhElectric"] then setVisibility(N["chassisMain_fhElectric"],false) end
if N["display_fh16"] then setVisibility(N["display_fh16"],true) end
if N["display_fhElectric"] then setVisibility(N["display_fhElectric"],false) end
if N["engine_fh16_decals"] then setVisibility(N["engine_fh16_decals"],true) end
if N["engine_fhElectric_decals"] then setVisibility(N["engine_fhElectric_decals"],false) end
if N["hoses_fhElectric"] then setVisibility(N["hoses_fhElectric"],false) end
if N["interior_fh16_decals"] then setVisibility(N["interior_fh16_decals"],true) end
if N["interior_fhElectric_decals"] then setVisibility(N["interior_fhElectric_decals"],false) end
if N.boxBody then delete(N.boxBody) end
local function prune(n) for i=getNumOfChildren(n)-1,0,-1 do local c=getChildAt(n,i); local name=getName(c); if not getVisibility(c) or string.find(name,"colPart") or string.find(name,"collision") then delete(c) else prune(c) end end end
prune(getRootNode())
source("C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/source/preview_body_wheels.lua")
clearSelection(); addSelection(N.fh16_main_component1); print("[FLATBED] configured scratch Volvo, wheels added, root selected")