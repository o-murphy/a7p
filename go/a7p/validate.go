package a7p

import (
	profedit "a7p-go/a7p/profedit"
	"fmt"

	protovalidate "github.com/bufbuild/protovalidate-go"
	validator "github.com/go-playground/validator/v10"
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
