package com.axelcurmi.eventreplayer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.stream.Collectors;

import com.google.gson.Gson;

public class EventReplayer {
	public static void main(String[] args) {
		String tracePath = "C:\\Users\\axelc\\Workspace\\MSc-Evaluation\\out\\rvtee\\20210511224016\\0.json";

		try {
			BufferedReader br = new BufferedReader(new FileReader(tracePath));
			String jsonString = br.lines().collect(Collectors.joining());
			
			Gson gson = new Gson();
			Event[] events = gson.fromJson(jsonString, Event[].class);
			
			for (Event event : events) {
				event.replay();
			}

			br.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
	}
}
