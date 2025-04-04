package tests

import (
	a7p "a7p-go/a7p"
	"a7p-go/a7p/profedit"
	"bytes"
	"fmt"
	"slices"
	"testing"

	validator "github.com/go-playground/validator/v10"
)

func TestSlice(t *testing.T) {
	s := []int32{100, 200}
	i := slices.Index(s, 0)
	fmt.Println("I", i)
}

func TestA7p(t *testing.T) {
	payload, err := a7p.Loads(TestingData, true)
	if err != nil {
		t.Errorf("Error %s", err)
	}
	fmt.Println(payload)

	dump, err := a7p.Dumps(payload, true)

	if err != nil {
		t.Errorf("Error %s", err)
	}

	// Compare if the dumped data matches the original TestingData
	if !bytes.Equal(dump, TestingData) {
		// Compare if the dumped data matches the original TestingData
		// Truncate the output to show only the first few bytes for diff
		maxDiffBytes := 50
		if len(TestingData) < maxDiffBytes {
			maxDiffBytes = len(TestingData)
		}
		t.Errorf("Data mismatch: expected first %v bytes: %v, but got: %v", maxDiffBytes, TestingData[:maxDiffBytes], dump[:maxDiffBytes])
	}
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

func TestValidator(t *testing.T) {
	protoPayload, _ := a7p.Load("../assets/example.a7p", true)

	payload := convertPayload(protoPayload)

	validate := validator.New()

	if err := validate.Struct(payload); err != nil {
		// t.Errorf("validation failed: %s", err)
		for _, e := range err.(validator.ValidationErrors) {
			fmt.Printf("Field: %s | Tag: %s | Value: %v\n", e.Field(), e.Tag(), e.Value())
		}
	}
}
