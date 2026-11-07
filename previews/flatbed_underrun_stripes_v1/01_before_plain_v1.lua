assert(type(flatbedView)=='function','Fitted scene required')
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
flatbedState('boards',false)
flatbedView(2,1.5,-9,0,.95,-5.3,30)
