package main

import (
	"fmt"
	"math"
	"time"
	"github.com/chobie/go-gaussian"
)

var norm = gaussian.NewGaussian(0, 1)

type vanillaOption struct {
	K        float64 // strike
	S        float64 // spot price
	r        float64 // risk free rate
	sigma    float64 // volatility
	evalDate string  // current date
	expDate  string  // expiry date
	Q        float64 // dividend yield
	T        float64 // Time in days btw exp_date and eval_date
	Type     string  // "C" or "P" for call or put respectively
	price    float64 // premium of option
	delta    float64 // delta of option
	gamma    float64 // gamma of option
	theta    float64 // theta of option
	vega     float64 // vega of option
}

func opt(Type, evalDate, expDate string, K, S, r, Q, price, sigma float64) *vanillaOption {
	o := &vanillaOption{
		K:        K,
		S:        S,
		r:        r,
		evalDate: evalDate,
		expDate:  expDate,
		T:        calculateT(evalDate, expDate),
		Q:        Q,
		Type:     Type,
		sigma:    sigma,
		price:    price,
	}
	o.Init()
	return o
}

func calculateT(evalDate string, expDate string) float64 {
	// Calculate the time to expiry for an option and return it in years
	// Time package uses 2006 jan 02 as reference fmt https://golang.org/src/time/format.go
	dtfmt := "20060102"
	evalDt, _ := time.Parse(dtfmt, evalDate)
	expDt, _ := time.Parse(dtfmt, expDate)
	return (expDt.Sub(evalDt).Hours() / 24) / 365.0
}

func (opt *vanillaOption) d1(impVol float64) float64 {
	return (math.Log(opt.S/opt.K) + opt.T*(opt.r-opt.Q+0.5*math.Pow(impVol, 2))) / (impVol * math.Sqrt(opt.T))
}

func (opt *vanillaOption) d2(impVol float64) float64 {
	return (opt.d1(impVol) - (impVol * math.Sqrt(opt.T)))
}

func (opt *vanillaOption) impliedVol() float64 {
	v := math.Sqrt(2*math.Pi/opt.T) * opt.price / opt.S
	//fmt.Printf(“ — initial vol: %v\n”, v)
	for i := 0; i < 100; i++ {
		d1 := opt.d1(v)
		d2 := opt.d2(v)
		vega := opt.S * norm.Pdf(d1) * math.Sqrt(opt.T)
		cp := 1.0
		if opt.Type == "P" {
			cp = -1.0
		}
		price0 := cp*opt.S*norm.Cdf(cp*d1) - cp*opt.K*math.Exp(-opt.r*opt.T)*norm.Cdf(cp*d2)
		v = v - (price0-opt.price)/vega
		//fmt.Printf(“ — next vol %v : %v / %v \n”, i, v,
		//             math.Pow(10, -25))
		if math.Abs(price0-opt.price) < math.Pow(10, -25) {
			break
		}
	}
	return v
}

func (opt *vanillaOption) Init() {
	if opt.sigma == -1 {
		opt.sigma = opt.impliedVol()
	}
	d1 := opt.d1(opt.sigma)
	d2 := opt.d2(opt.sigma)
	nPrime := math.Pow(math.Sqrt(2*math.Pi), -1) * math.Exp(-0.5*math.Pow(d1, 2))
	qDisc := math.Exp(-opt.Q * opt.T)
	rDisc := math.Exp(-opt.r * opt.T)
	switch {
	case opt.Type == "C":
		fmt.Println(norm.Cdf(d1))
		opt.price = norm.Cdf(d1)*opt.S*qDisc - norm.Cdf(d2)*opt.K*rDisc
		opt.delta = qDisc * norm.Cdf(d1)
		opt.theta = (-nPrime*0.5*opt.S*opt.sigma/math.Sqrt(opt.T) - opt.r*opt.K*rDisc*norm.Cdf(d2)) / 365
		//1 / 252 * (-(opt.S * qDisc * nPrime * opt.sigma / (2 * math.Sqrt(opt.T))) - (opt.r * opt.K * rDisc * norm.Cdf(d2)))
	case opt.Type == "P":
		opt.price = (opt.K * norm.Cdf(-d2) * rDisc) - (opt.S * norm.Cdf(-d1) * qDisc)
		opt.delta = qDisc * (norm.Cdf(d1) - 1)
		opt.theta = (-nPrime*0.5*opt.S*opt.sigma/math.Sqrt(opt.T) + opt.r*opt.K*rDisc*norm.Cdf(-d2)) / 365
	default:
		fmt.Println("Option type is not recognised. \nPlease use C or P for call and P respectively")
	}
	opt.gamma = nPrime * qDisc / (opt.S * opt.sigma * math.Sqrt(opt.T))
	opt.vega = 0.01 * opt.S * qDisc * math.Sqrt(opt.T) * nPrime
}

func main() {
	mockOption := opt("P", "20200510", "20210510", 280, 280, 0.05, 0, 26.191744957864472, -1)
	fmt.Printf("Price: %g\nDelta: %g\nGamma: %g\nTheta: %g\nVega: %g", mockOption.price, mockOption.delta, mockOption.gamma, mockOption.theta, mockOption.vega)
}
