package a7p

import (
	profedit "a7p-go/a7p/profedit"
	"fmt"

	protovalidate "github.com/bufbuild/protovalidate-go"
	validator "github.com/go-playground/validator/v10"
)

type DistanceType string

var Distances = map[DistanceType][]int32{
	SubsonicRange: {25, 50, 75, 100, 110, 120, 130, 140, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220,
		225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315, 320, 325, 330,
		335, 340, 345, 350, 355, 360, 365, 370, 375, 380, 385, 390, 395, 400},
	LowRange: {100, 150, 200, 225, 250, 275, 300, 320, 340, 360, 380, 400, 410, 420, 430, 440,
		450, 460, 470, 480, 490, 500, 505, 510, 515, 520, 525, 530, 535, 540, 545, 550,
		555, 560, 565, 570, 575, 580, 585, 590, 595, 600, 605, 610, 615, 620, 625, 630,
		635, 640, 645, 650, 655, 660, 665, 670, 675, 680, 685, 690, 695, 700},
	MediumRange: {100, 200, 250, 300, 325, 350, 375, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640,
		650, 660, 670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 805, 810, 815, 820, 825, 830,
		835, 840, 845, 850, 855, 860, 865, 870, 875, 880, 885, 890, 895, 900, 905, 910, 915, 920, 925, 930, 935, 940,
		945, 950, 955, 960, 965, 970, 975, 980, 985, 990, 995, 1000},
	LongRange: {100, 200, 250, 300, 350, 400, 420, 440, 460, 480, 500, 520, 540, 560, 580, 600, 610, 620, 630, 640, 650, 660,
		670, 680, 690, 700, 710, 720, 730, 740, 750, 760, 770, 780, 790, 800, 810, 820, 830, 840, 850, 860, 870, 880,
		890, 900, 910, 920, 930, 940, 950, 960, 970, 980, 990, 1000, 1005, 1010, 1015, 1020, 1025, 1030, 1035, 1040,
		1045, 1050, 1055, 1060, 1065, 1070, 1075, 1080, 1085, 1090, 1095, 1100, 1105, 1110, 1115, 1120, 1125, 1130,
		1135, 1140, 1145, 1150, 1155, 1160, 1165, 1170, 1175, 1180, 1185, 1190, 1195, 1200, 1205, 1210, 1215, 1220,
		1225, 1230, 1235, 1240, 1245, 1250, 1255, 1260, 1265, 1270, 1275, 1280, 1285, 1290, 1295, 1300, 1305, 1310,
		1315, 1320, 1325, 1330, 1335, 1340, 1345, 1350, 1355, 1360, 1365, 1370, 1375, 1380, 1385, 1390, 1395, 1400,
		1405, 1410, 1415, 1420, 1425, 1430, 1435, 1440, 1445, 1450, 1455, 1460, 1465, 1470, 1475, 1480, 1485, 1490,
		1495, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565, 1570, 1575, 1580,
		1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655, 1660, 1665, 1670,
		1675, 1680, 1685, 1690, 1695, 1700},
	UltraRange: {100, 200, 250, 300, 350, 400, 450, 500, 520, 540, 560, 580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780,
		800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000, 1010, 1020, 1030, 1040, 1050, 1060, 1070, 1080, 1090,
		1100, 1110, 1120, 1130, 1140, 1150, 1160, 1170, 1180, 1190, 1200, 1210, 1220, 1230, 1240, 1250, 1260, 1270,
		1280, 1290, 1300, 1310, 1320, 1330, 1340, 1350, 1360, 1370, 1380, 1390, 1400, 1410, 1420, 1430, 1440, 1450,
		1460, 1470, 1480, 1490, 1500, 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565,
		1570, 1575, 1580, 1585, 1590, 1595, 1600, 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655,
		1660, 1665, 1670, 1675, 1680, 1685, 1690, 1695, 1700, 1705, 1710, 1715, 1720, 1725, 1730, 1735, 1740, 1745,
		1750, 1755, 1760, 1765, 1770, 1775, 1780, 1785, 1790, 1795, 1800, 1805, 1810, 1815, 1820, 1825, 1830, 1835,
		1840, 1845, 1850, 1855, 1860, 1865, 1870, 1875, 1880, 1885, 1890, 1895, 1900, 1905, 1910, 1915, 1920, 1925,
		1930, 1935, 1940, 1945, 1950, 1955, 1960, 1965, 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015,
		2020, 2025, 2030, 2035, 2040, 2045, 2050, 2055, 2060, 2065},
}

const (
	SubsonicRange DistanceType = "subsonic"
	LowRange      DistanceType = "low"
	MediumRange   DistanceType = "medium"
	LongRange     DistanceType = "long"
	UltraRange    DistanceType = "ultra"
)

const SwitchesMaxCount = 4

// Validate checks the content using protovalidate.
func ValidateProto(payload *profedit.Payload) error {
	validator, err := protovalidate.New()
	if err != nil {
		return fmt.Errorf("failed to create validator: %w", err)
	}

	if err := validator.Validate(payload); err != nil {
		return fmt.Errorf("validation failed: %w", err)
	}
	return nil
}

func ValidateSpec(payload *profedit.Payload) error {
	pld := convertPayload(payload)

	validate := validator.New()

	if err := validate.Struct(pld); err != nil {
		// t.Errorf("validation failed: %s", err)
		for _, e := range err.(validator.ValidationErrors) {
			fmt.Printf("Field: %s | Tag: %s | Value: %v\n", e.Field(), e.Tag(), e.Value())
		}
		return err
	}
	return nil
}

type swPosT struct {
	cIdx         int32
	reticleIdx   int32
	zoom         int32 `validate:"gte=1,lte=6"`
	distance     int32
	distanceFrom profedit.DType
}

type coefRowT struct {
	bcCd int32
	mv   int32
}

type profileT struct {
	profileName   string `validate:"max=50"`
	cartridgeName string `validate:"max=50"`
	bulletName    string `validate:"max=50"`
	shortNameTop  string `validate:"max=8"`
	shortNameBot  string `validate:"max=8"`
	userNote      string `validate:"max=250"`

	zeroX    int32 `validate:"gte=-600000,lte=600000"`
	zeroY    int32 `validate:"gte=-600000,lte=600000"`
	scHeight int32 `validate:"gte=-5000,lte=5000"`
	rTwist   int32 `validate:"gte=0,lte=10000"`

	cMuzzleVelocity     int32 `validate:"gte=100,lte=30000"`
	cZeroTemperature    int32 `validate:"gte=-100,lte=100"`
	cTCoeff             int32 `validate:"gte=2,lte=3000"`
	cZeroDistanceIdx    int32 `validate:"gte=0,lte=200"`
	cZeroAirTemperature int32 `validate:"gte=-100,lte=100"`
	cZeroAirPressure    int32 `validate:"required"`
	cZeroAirHumidity    int32 `validate:"gte=0,lte=100"`
	cZeroWPitch         int32 `validate:"gte=-90,lte=90"`
	cZeroPTemperature   int32 `validate:"gte=-100,lte=100"`

	bDiameter int32 `validate:"gte=1,lte=65535"`
	bWeight   int32 `validate:"gte=10,lte=65535"`
	bLength   int32 `validate:"gte=1,lte=10000"`

	twistDir   profedit.TwistDir `validate:""`
	bcType     profedit.GType    `validate:""`
	switches   []*swPosT         `validate:"required,min=1,max=4"`
	distances  []int32           `validate:"required,min=4,max=200"`
	coefRows   []*coefRowT       `validate:"required,min=1,max=200"`
	caliber    string            `validate:"max=50"`
	deviceUuid string            `validate:"max=50"`
}

type payloadT struct {
	profile *profileT `validate:"required"`
}

//

func convertPayload(payload *profedit.Payload) payloadT {
	return payloadT{profile: convertProfile(payload.Profile)}
}

func convertProfile(profile *profedit.Profile) *profileT {
	return &profileT{
		profileName:         profile.ProfileName,
		cartridgeName:       profile.CartridgeName,
		bulletName:          profile.BulletName,
		shortNameTop:        profile.ShortNameTop,
		shortNameBot:        profile.ShortNameBot,
		userNote:            profile.UserNote,
		zeroX:               profile.ZeroX,
		zeroY:               profile.ZeroY,
		scHeight:            profile.ScHeight,
		rTwist:              profile.RTwist,
		cMuzzleVelocity:     profile.CMuzzleVelocity,
		cZeroTemperature:    profile.CZeroTemperature,
		cTCoeff:             profile.CTCoeff,
		cZeroDistanceIdx:    profile.CZeroDistanceIdx,
		cZeroAirTemperature: profile.CZeroAirTemperature,
		cZeroAirPressure:    profile.CZeroAirPressure,
		cZeroAirHumidity:    profile.CZeroAirHumidity,
		cZeroWPitch:         profile.CZeroWPitch,
		cZeroPTemperature:   profile.CZeroPTemperature,
		bDiameter:           profile.BDiameter,
		bWeight:             profile.BWeight,
		bLength:             profile.BLength,
		twistDir:            profile.TwistDir,
		bcType:              profile.BcType,
		switches:            convertSwPos(profile.Switches),
		distances:           profile.Distances,
		coefRows:            convertCoefRows(profile.CoefRows),
		caliber:             profile.Caliber,
		deviceUuid:          profile.DeviceUuid,
	}
}

// Convert nested types
func convertSwPos(switches []*profedit.SwPos) []*swPosT {
	var result []*swPosT
	for _, s := range switches {
		result = append(result, &swPosT{
			cIdx:         s.CIdx,
			reticleIdx:   s.ReticleIdx,
			zoom:         s.Zoom,
			distance:     s.Distance,
			distanceFrom: s.DistanceFrom,
		})
	}
	return result
}

func convertCoefRows(coefRows []*profedit.CoefRow) []*coefRowT {
	var result []*coefRowT
	for _, r := range coefRows {
		result = append(result, &coefRowT{
			bcCd: r.BcCd,
			mv:   r.Mv,
		})
	}
	return result
}
