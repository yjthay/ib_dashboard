package pricer

import (
	"fmt"
	"math"
	"time"

	"github.com/chobie/go-gaussian"
)

var norm = gaussian.NewGaussian(0, 1)

// VanillaOption is a struct that creates a container holding all the information of any option
type VanillaOption struct {
	Strike       float64 `json:"strike"`       // strike
	Spot         float64 `json:"spot"`         // spot
	RiskFreeRate float64 `json:"riskFreeRate"` // risk free rate
	Sigma        float64 `json:"sigma"`        // volatility
	EvalDate     string  `json:"evalDate"`     // current date
	ExpDate      string  `json:"expDate"`      // expiry date
	Q            float64 `json:"divYield"`     // dividend yield
	T            float64 `json:"timeToExpiry"` // Time in days btw exp_date and eval_date
	Type         string  `json:"type"`         // "C" or "P" for call or put respectively
	Price        float64 `json:"price"`        // premium of option
	Delta        float64 `json:"delta"`        // Delta of option
	Gamma        float64 `json:"gamma"`        // Gamma of option
	Theta        float64 `json:"theta"`        // Theta of option
	Vega         float64 `json:"vega"`         // Vega of option
}

// Opt is a function initialise an option and generate the associated risk metrics with it
func Opt(Type, EvalDate, ExpDate string, Strike, Spot, RiskFreeRate, Q, Price, Sigma float64) *VanillaOption {
	o := &VanillaOption{
		Strike:       Strike,
		Spot:         Spot,
		RiskFreeRate: RiskFreeRate,
		EvalDate:     EvalDate,
		ExpDate:      ExpDate,
		T:            calculateT(EvalDate, ExpDate),
		Q:            Q,
		Type:         Type,
		Sigma:        Sigma,
		Price:        Price,
	}
	o.init()
	return o
}

func calculateT(EvalDate string, ExpDate string) float64 {
	// Calculate the time to expiry for an option and return it in years
	// Time package uses 2006 Jan 02 as reference fmt https://golang.org/src/time/format.go
	dtfmt := "20060102"
	evalDt, _ := time.Parse(dtfmt, EvalDate)
	expDt, _ := time.Parse(dtfmt, ExpDate)
	return (expDt.Sub(evalDt).Hours() / 24) / 365.0
}

func (opt *VanillaOption) d1(impVol float64) float64 {
	return (math.Log(opt.Spot/opt.Strike) + opt.T*(opt.RiskFreeRate-opt.Q+0.5*math.Pow(impVol, 2))) / (impVol * math.Sqrt(opt.T))
}

func (opt *VanillaOption) d2(impVol float64) float64 {
	return (opt.d1(impVol) - (impVol * math.Sqrt(opt.T)))
}

func (opt *VanillaOption) impliedVol() float64 {
	// Using Newton Raphson Method https://en.wikipedia.org/wiki/Newton%27s_method#Description
	// Can make further refinements to ensure that the initialisation step is done even better
	v := math.Sqrt(2*math.Pi/opt.T) * opt.Price / opt.Spot
	//fmt.Printf(“ — initial vol: %v\n”, v)
	for i := 0; i < 100; i++ {
		d1 := opt.d1(v)
		d2 := opt.d2(v)
		Vega := opt.Spot * norm.Pdf(d1) * math.Sqrt(opt.T)
		cp := 1.0
		if opt.Type == "P" {
			cp = -1.0
		}
		price0 := cp*opt.Spot*norm.Cdf(cp*d1) - cp*opt.Strike*math.Exp(-opt.RiskFreeRate*opt.T)*norm.Cdf(cp*d2)
		v = v - (price0-opt.Price)/Vega
		//fmt.Printf(“ — next vol %v : %v / %v \n”, i, v,
		//             math.Pow(10, -25))
		if math.Abs(price0-opt.Price) < math.Pow(10, -25) {
			break
		}
	}
	return v
}

func (opt *VanillaOption) init() {
	if opt.Sigma == -1 {
		opt.Sigma = opt.impliedVol()
	}
	d1 := opt.d1(opt.Sigma)
	d2 := opt.d2(opt.Sigma)
	nPrime := math.Pow(math.Sqrt(2*math.Pi), -1) * math.Exp(-0.5*math.Pow(d1, 2))
	qDisc := math.Exp(-opt.Q * opt.T)
	rDisc := math.Exp(-opt.RiskFreeRate * opt.T)
	switch {
	case opt.Type == "C":
		// fmt.Println(norm.Cdf(d1))
		opt.Price = norm.Cdf(d1)*opt.Spot*qDisc - norm.Cdf(d2)*opt.Strike*rDisc
		opt.Delta = qDisc * norm.Cdf(d1)
		opt.Theta = (-nPrime*0.5*opt.Spot*opt.Sigma/math.Sqrt(opt.T) - opt.RiskFreeRate*opt.Strike*rDisc*norm.Cdf(d2)) / 365
		//1 / 252 * (-(opt.Spot * qDisc * nPrime * opt.Sigma / (2 * math.Sqrt(opt.T))) - (opt.RiskFreeRate * opt.Strike * rDisc * norm.Cdf(d2)))
	case opt.Type == "P":
		opt.Price = (opt.Strike * norm.Cdf(-d2) * rDisc) - (opt.Spot * norm.Cdf(-d1) * qDisc)
		opt.Delta = qDisc * (norm.Cdf(d1) - 1)
		opt.Theta = (-nPrime*0.5*opt.Spot*opt.Sigma/math.Sqrt(opt.T) + opt.RiskFreeRate*opt.Strike*rDisc*norm.Cdf(-d2)) / 365
	default:
		fmt.Println("Option type is not recognised. \nPlease use C or P for call and P respectively")
	}
	opt.Gamma = nPrime * qDisc / (opt.Spot * opt.Sigma * math.Sqrt(opt.T))
	opt.Vega = 0.01 * opt.Spot * qDisc * math.Sqrt(opt.T) * nPrime
}

// func main() {
// 	mockOption := opt("P", "20200510", "20210510", 280, 280, 0.05, 0, 26.191744957864472, -1)
// 	fmt.Printf("Price: %g\nDelta: %g\nGamma: %g\nTheta: %g\nVega: %g", mockOption.Price, mockOption.Delta, mockOption.Gamma, mockOption.Theta, mockOption.Vega)
// }
