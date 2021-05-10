package com.axelcurmi.eventreplayer;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.stream.Collectors;

import com.google.gson.Gson;

public class EventReplayer {
	public static void main(String[] args) {
		if (args.length < 1 || args.length > 1) {
			System.out.println(
					"usage: event-replayer <FILE>\n\n" +
					"Replay events from a given trace file\n\n" +
					"positional arguments:\n" +
					"  FILE: The trace file to replay events from");
			System.exit(1);
		}

		try {
			BufferedReader br = new BufferedReader(new FileReader(args[0]));
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
