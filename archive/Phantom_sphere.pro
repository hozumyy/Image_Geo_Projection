
window,2,xs=500,ys=500

;define the location of Yucca Ridge and CSU at geographic coordinates
lat0=40.7 ;Yucca Ridge latitude
lon0=-104.9 ;Yucca Ridge longitude
earthradius=6378.0 ;km
circ=2.0*!pi*earthradius
deglatperkm=360.0/circ
radlat=earthradius*cos(lat0*!pi/180.0)
circlat=2.0*!pi*radlat
deglonperkm=360.0/circlat
DEVICE, DECOMPOSED = 0

read_png, '/research/tiger elves/draft/GW Elve_12JUN13_0359.13.526Z.png',ph   ;load picture
xs = fix(800.0/1.0) ;x pixel
ys = fix(600.0/1.0) ;y pixel

az = fltarr(xs,ys)   ;azimuth
el = fltarr(xs,ys) ;elevation angle
r = fltarr(xs,ys)  ; horizontal radius
xgeo = fltarr(xs,ys)   ;geographic x
ygeo = fltarr(xs,ys)   ;geographic y
a_an= fltarr(xs,ys)
b_an = fltarr(xs,ys)
c_an = fltarr(xs,ys)

for i=0,xs-1 do begin
    for j=0,ys-1 do begin
       el(i,j) = (2.3)/180.*!pi+(j-600/2.)/600.*19.2/180.*!pi   ;calculate elevation angle for each pixel angle = 2*atan(d/2f)
       az(i,j) = 24.9/180.*!pi+(i-800/2.)/800.*25.1/180.*!pi   ;calculate azimuth angle for each pixel angle = 2*atan(d/2f)
       ;if el(i,j) le 0 then el(i,j) = 0.0000001
    endfor
Endor

A = 6370.+1.5
C= 6370+75.
c_an= !pi/2.+el
a_an=asin((A/C)*sin(c_an))
b_an=!pi-a_an-c_an
r=6370.*b_an


ygeo = r*cos(az)
xgeo = r*sin(az)
triangulate, double(xgeo),double(ygeo),tr,b
wrap2=fltarr(2001,2001)
wrap2 = trigrid(xgeo,ygeo,ph(0,*,*),tr, [1,1],[-1000,-1000,1000,1000],xgrid=xg,ygrid=yg)

xlon=xg*deglonperkm+lon0
ylat=yg*deglatperkm+lat0
wset,2
map_set,lat0,lon0,limit=[40.,-106,48,-96],/ortho,/iso
result = map_image(bytscl(wrap2,max=50, MIN=30,TOP=!D.TABLE_SIZE),startx,starty,latmin=ylat[0],latmax=ylat[2000],lonmin=xlon[0],lonmax=xlon[2000],/bilinear,compress=1)
tvscl,result,startx,starty
map_continents,/USA,MLINETHICK=3
map_grid,latdel=1,londel=1,/label,lonlab=40.5,latlab=-105.5,charsize=1.5,glinethick=2
wimage=tvrd()

write_png,'/research/tiger elves/projected phantom image_re sprite.png',wimage


pause
END
