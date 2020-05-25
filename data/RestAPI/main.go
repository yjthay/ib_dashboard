package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"reflect"
	"strconv"

	"github.com/gorilla/mux"
	"github.com/yjthay/ib_dashboard/data/RestAPI/pricer"
)

var portfolio []pricer.VanillaOption

func main() {
	router := mux.NewRouter()
	portfolio = append(portfolio, pricer.VanillaOption{Strike: 280, Spot: 280, RiskFreeRate: 0.05,
		Price: 39.847556, EvalDate: "20200517", ExpDate: "20201217", Type: "C"})
	portfolio = append(portfolio, pricer.VanillaOption{Strike: 280, Spot: 280, RiskFreeRate: 0.05,
		Price: 26.191795, EvalDate: "20200517", ExpDate: "20201217", Type: "P"})
	router.HandleFunc("/api/opts/keys", getOptKeys).Methods("GET")
	router.HandleFunc("/api/opts/greek/keys", getGreekKeys).Methods("GET")
	router.HandleFunc("/api/opts", getAllOpts).Methods("GET")
	router.HandleFunc("/api/opts/{id}", getOpt).Methods("GET")
	router.HandleFunc("/api/opts", createOpt).Methods("POST")
	router.HandleFunc("/api/opts/{id}", deleteOpt).Methods("DELETE")
	router.HandleFunc("/api/opts/{id}", updateOpt).Methods("PUT")

	fmt.Println("Starting up server...")
	log.Fatal(http.ListenAndServe(":7777", router))
}

// Create a key for Greek struct
func getGreekKeys(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var emptyGreek pricer.Greek
	var output []string
	typ := reflect.TypeOf(emptyGreek)
	for i := 0; i < typ.NumField(); i++ {
		output = append(output, typ.Field(i).Tag.Get("json"))
	}
	json.NewEncoder(w).Encode(output)
}

// Create a key for VanillaOpt struct
func getOptKeys(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var emptyOpt pricer.VanillaOption
	var output []string
	val := reflect.ValueOf(emptyOpt)
	for i := 0; i < val.Type().NumField(); i++ {
		output = append(output, val.Type().Field(i).Tag.Get("json"))
	}
	json.NewEncoder(w).Encode(output)
}

// Get all options
func getAllOpts(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	for id, opt := range portfolio {
		output := *pricer.Opt(opt.Type, opt.EvalDate, opt.ExpDate,
			opt.Strike, opt.Spot, opt.RiskFreeRate, opt.Q, opt.Price, -1)
		portfolio[id] = output
	}
	json.NewEncoder(w).Encode(portfolio)
	return
}

// Get a single specific option
func getOpt(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, err := strconv.Atoi(params["id"])
	if err != nil {
		w.WriteHeader(400)
		w.Write([]byte("ID could not be converted to integer"))
		return
	}
	if id >= len(portfolio) {
		w.WriteHeader(404)
		w.Write([]byte("No option found with specified ID"))
		return
	}
	for id, opt := range portfolio {
		output := *pricer.Opt(opt.Type, opt.EvalDate, opt.ExpDate,
			opt.Strike, opt.Spot, opt.RiskFreeRate, opt.Q, opt.Price, -1)
		portfolio[id] = output
	}
	opt := portfolio[id]
	json.NewEncoder(w).Encode(opt)
}

// Create an option
func createOpt(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	var opt pricer.VanillaOption
	json.NewDecoder(r.Body).Decode(&opt)
	portfolio = append(portfolio, opt)
	json.NewEncoder(w).Encode(opt)
}

// Delete an option
func deleteOpt(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, err := strconv.Atoi(params["id"])
	if err != nil {
		w.WriteHeader(400)
		w.Write([]byte("ID could not be converted to integer"))
		return
	}
	if id >= len(portfolio) {
		w.WriteHeader(404)
		w.Write([]byte("No option found with specified ID"))
		return
	}
	portfolio = append(portfolio[:id], portfolio[id+1:]...)
	json.NewEncoder(w).Encode(portfolio)
}

// Update an option
func updateOpt(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	params := mux.Vars(r)
	id, err := strconv.Atoi(params["id"])
	if err != nil {
		w.WriteHeader(400)
		w.Write([]byte("ID could not be converted to integer"))
		return
	}
	if id >= len(portfolio) {
		w.WriteHeader(404)
		w.Write([]byte("No option found with specified ID"))
		return
	}
	opt := &portfolio[id]
	json.NewDecoder(r.Body).Decode(opt)
	json.NewEncoder(w).Encode(opt)
}
