# Gathered curtain attachment correction

The user's in-game screenshot showed the original straight gathered pleats. The local game log at 16:28:56 confirmed that gatheredCurtains.i3d loaded, followed by link errors at BoxTruckBody.lua:153: expected Int, actual Table. The original visuals therefore remained visible.

Cause: the loader passed self.i3dMappings[name] directly to link. FS25 mapping records contain the scene handle in .nodeId, as confirmed in the installed gameSource.zip precisionFarming specializations (CropSensor and ExtendedSprayerEffects).

Corrected the loader to use mapping.nodeId. Corrected the regression fixture to wrap mapped nodes in {nodeId=parent}, and added a link assertion that rejects mapping records. The full existing Lua/asset regression suite passes using the existing local Lupa runtime. Earlier mocks incorrectly represented mappings as scene nodes and missed this integration bug.

No visual redesign, packaging, installation, or upload performed. Source fix still needs an actual in-game reload after a requested build/deployment. The delivered 1.3.0.0 ZIP remains the previous build.
