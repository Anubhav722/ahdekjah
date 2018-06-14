package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
)

type FbMessage struct {
	Text string `json:"text"`
}

type Recipient struct {
	ID string `json:"id"`
}

func main() {
	http.HandleFunc("/webhook/", webhook)
	http.ListenAndServe(":8080", nil)
}

func webhook(w http.ResponseWriter, req *http.Request) {
	if err := req.ParseForm(); err != nil {
		log.Fatal(err)
	}
	fmt.Println(req.Form)
	w.Header().Set("Content-Type", "text/plain")
	fmt.Fprintf(w, "success")

	// decode body - received message
	var resp interface{}

	json.NewDecoder(req.Body).Decode(&resp)
	fmt.Println(resp)

	// send message
	message := map[string]interface{}{
		"recipient": Recipient{ID: "151761822056974"},
		"message":   FbMessage{Text: "I'm new here. Haven't learned much words yet."},
	}
	if err := sendMessage(message); err != nil {
		log.Println(err)
	}
	return
}

func sendMessage(message map[string]interface{}) error {
	url := "https://graph.facebook.com/v2.6/me/messages"
	page_token := "EAAWBsuDybjkBABDpUR8VOdJMqsVSuMRvLXDwsUBuVqcEGtZAVZCAHN5anHcnPM9TZCMirAXUO1qFBOVFbsiK8ZC67mmIOcpiCqPMmxAmujGBeDNo93zeSaLaiuFRLOZA4QxKfCO7NQRKjXa1DbaoLncBRsbSKV6cxSShxIKpbWExMZCSTCTCNq"
	url += "?access_token=" + page_token
	data, _ := json.Marshal(message) // ignore error for now
	fmt.Println("data: ", string(data))
	fmt.Println("url: ", url)
	resp, err := http.Post(url, "application/json", bytes.NewReader(data))
	if err != nil {
		return err
	}
	fmt.Println("status: ", resp.Status)
	buf := make([]byte, resp.ContentLength)
	io.ReadFull(resp.Body, buf)
	fmt.Println("body: ", string(buf))
	return nil
}
