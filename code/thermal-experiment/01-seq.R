library(Thermimage)
library(RcppCNPy)
library(data.table)
library(stringr)

## Convert thermal imaging camera files(.SEQ) to python files(.npy)

base_dir = "./data/moth-FLIR-ori-cold/"
SEQs = list.files(base_dir)

length(SEQs)

for (n in SEQs) {
  if (substr(n, str_length(n)-3, str_length(n)) != '.SEQ') {
    continue
  }
  v = paste0(base_dir, n)
  camvals = flirsettings(v)
  w = camvals$Info$RawThermalImageWidth
  h = camvals$Info$RawThermalImageHeight
  print(c(w,h)) # should be 320 * 240
  
  # According to the specs, we know the working height is a little bit smaller
  img_w = w
  img_h = h - 6
  
  templookup = raw2temp(raw=0:65535, E=camvals$Info$Emissivity, OD=camvals$Info$ObjectDistance, RTemp=camvals$Info$ReflectedApparentTemperature, ATemp=camvals$Info$AtmosphericTemperature, IRWTemp=camvals$Info$IRWindowTemperature, IRT=camvals$Info$IRWindowTransmission, RH=camvals$Info$RelativeHumidity, PR1=camvals$Info$PlanckR1,PB=camvals$Info$PlanckB,PF=camvals$Info$PlanckF,PO=camvals$Info$PlanckO,PR2=camvals$Info$PlanckR2)
  templookup[is.nan(templookup)] = -999
  # 
  ##### FrameLocates Hack #####
  # Extract metadata and describe data blocks
  vidfile = v
  
  f.start = NULL
  h.start = NULL
  w.hex.be = formatC(as.character(as.hexmode(w), width = 4, format = "s"))
  h.hex.be = formatC(as.character(as.hexmode(h), width = 4, format = "s"))
  w.hex.le = c(substr(w.hex.be, 3, 4), substr(w.hex.be, 1, 2))
  h.hex.le = c(substr(h.hex.be, 3, 4), substr(h.hex.be, 1, 2))
  #l = w * h
  finfo = file.info(vidfile)
  byte.length = 1
  to.read = file(vidfile, "rb")
  alldata = readBin(to.read, raw(), n = 5e+06, size = 1)
  close(to.read)
  fid = c("02", "00", w.hex.le, h.hex.le)
  wh.locate = locate.fid(fid, alldata, long = TRUE, zeroindex = TRUE)
  diff.wh.locate = diff(wh.locate)
  gaps = unique(diff.wh.locate)
  no.unique.locates = length(gaps)
  
  # Find the right position for the header, which is 1
  right_head_on = 1
  
  # Find the right position for the thermal frame, which is 2
  right_frame_on = 2
  
  ##### Get timestamp positions and frame positions #####
  repeats = finfo$size/sum(gaps)
  
  h.start = wh.locate[right_head_on]
  h.interval = wh.locate[right_head_on+no.unique.locates] - wh.locate[right_head_on]
  head_pos = h.start + cumsum(c(0, rep(h.interval, repeats-1)))
  
  f.start = wh.locate[right_frame_on]
  f.interval = wh.locate[right_frame_on+no.unique.locates] - wh.locate[right_frame_on]
  frame_pos = f.start + cumsum(c(0, rep(f.interval, repeats-1)))
  
  first_frame_ts = as.numeric(as.POSIXct(getTimes(head_pos[1], vidfile=v)))
  last_frame_ts = as.numeric(as.POSIXct(getTimes(head_pos[length(head_pos)], vidfile=v)))
  frame_rate = length(head_pos) / (last_frame_ts - first_frame_ts)
  
  # all thermal
  next_start = 1
  #for (i in 150000:150500) {
  ptm <- proc.time()
  for (i in 1:length(head_pos)) {
    #for (i in 1:1000) {
    ts = getTimes(head_pos[i], vidfile=v)
    reformatted_ts = str_sub(str_replace_all(ts, replacement='.', pattern=':'), 1, 19)
    fname = paste0(str_replace_all(ts, replacement='_', pattern=':|\\s|\\.|\\+'), '.npy')
    fr = getFrames(frame_pos[i], vidfile=v, w=img_w, h=img_h)
    fr_temp = templookup[fr+1]
    
    viz_dir = paste0('./data/moth-FLIR/moth-FLIR-viz-cold_/', n, '/')
    npy_dir = paste0('./data/moth-FLIR/moth-FLIR-viz-cold_/', n, '/npy/')
    if (!dir.exists(npy_dir)) {
      dir.create(npy_dir, showWarnings=TRUE, recursive=TRUE, mode = "0777")
    }
    save_path = paste0(npy_dir, fname)
    npySave(matrix(fr_temp, nrow=img_w), filename=save_path)
  }
  proc.time() - ptm
}
