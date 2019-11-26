//webkitURL is deprecated but nevertheless
(function(){

	URL = window.URL || window.webkitURL;
	
	var gumStream; 						//stream from getUserMedia()
	var recorder; 						//WebAudioRecorder object
	var input; 							//MediaStreamAudioSourceNode  we'll be recording
	var encodingType; 					//holds selected encoding for resulting audio (file)
	var encodeAfterRecord = true; 
	var recordingBlob = null;      // when to encode
	
	// shim for AudioContext when it's not avb. 
	var AudioContext = window.AudioContext || window.webkitAudioContext;
	var audioContext; //new audio context to help us record
	
	var encodingTypeSelect = document.getElementById("encodingTypeSelect");
	var recordButton = document.getElementById("recordButton");
	var stopButton = document.getElementById("stopButton");
	
	var wavesurfer = WaveSurfer.create({
		container: '#waveform',
		waveColor: 'violet',
		progressColor: 'purple',
		backgroundColor:'black'
	});
	//add events to those 2 buttons
	recordButton.addEventListener("click", startRecording);
	stopButton.addEventListener("click", stopRecording);
	registerServerListener();
	
	function startRecording() {
		console.log("startRecording() called");
		
		var constraints = { audio: true, video: false }
		
		navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
			__log("getUserMedia() success, stream created, initializing WebAudioRecorder...");

		
			audioContext = new AudioContext();

			//update the format 
			document.getElementById("formats").innerHTML = "Format: 2 channel " + encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value + " @ " + audioContext.sampleRate / 1000 + "kHz"

			//assign to gumStream for later use
			gumStream = stream;

			/* use the stream */
			input = audioContext.createMediaStreamSource(stream);

			//stop the input from playing back through the speakers
			

			//get the encoding 
			encodingType = encodingTypeSelect.options[encodingTypeSelect.selectedIndex].value;

			//disable the encoding selector
			encodingTypeSelect.disabled = true;

			recorder = new WebAudioRecorder(input, {
				workerDir: "static/js/", // must end with slash
				encoding: encodingType,
				numChannels: 2, //2 is the default, mp3 encoding supports only 2
				onEncoderLoading: function (recorder, encoding) {
					// show "loading encoder..." display
					__log("Loading " + encoding + " encoder...");
				},
				onEncoderLoaded: function (recorder, encoding) {
					// hide "loading encoder..." display
					__log(encoding + " encoder loaded");
				}
			});

			recorder.onComplete = function (recorder, blob) {
				__log("Encoding complete");
				createDownloadLink(blob, recorder.encoding);
				encodingTypeSelect.disabled = false;
				$('#audioform').trigger('submit');
			}

			recorder.setOptions({
				timeLimit: 120,
				encodeAfterRecord: encodeAfterRecord,
				ogg: { quality: 0.5 },
				mp3: { bitRate: 160 }
			});

			//start the recording process
			recorder.startRecording();

			__log("Recording started");

		}).catch(function (err) {
			//enable the record button if getUSerMedia() fails
			recordButton.disabled = false;
			stopButton.disabled = true;

		});

		//disable the record button
		recordButton.disabled = true;
		stopButton.disabled = false;
	}
	
	function stopRecording() {
		console.log("stopRecording() called");
		
		//stop microphone access
		gumStream.getAudioTracks()[0].stop();
	
		//disable the stop button
		stopButton.disabled = true;
		recordButton.disabled = false;
		
		//tell the recorder to finish the recording (stop recording + encode the recorded audio)
		recorder.finishRecording();
	
		__log('Recording stopped');
	}
	
	function createDownloadLink(blob,encoding) {
		console.log("Create download link")
		var url = URL.createObjectURL(blob);
		//var au = document.createElement('audio');
		var au = document.getElementById("audioplayer");
		var li = document.createElement('li');
		var link = document.createElement('a');
	
		//add controls to the <audio> element
		au.controls = true;
		au.src = url;
	
		//link the a element to the blob
		link.href = url;
		console.log("link.href called"+ link);
		link.download = new Date().toISOString() + '.'+ encoding;
	
		link.innerHTML = link.download;
		recordingBlob = blob;
		//var save = function() {
		/*console.log("Save function called")
		var form = new formData();
		form.append('file',recordingBlob, link.download);
		form.append('title','test');
		$.ajax({
			type: 'POST',
				url: '/save-record',
				data: form,
				cache: false,
				processData: false,
				contentType: false,
				}).done(function(data){
					console.log(data);
				});*/
		//};

		//add the new audio and a elements to the li element
	
		li.appendChild(link);
		wavesurfer.loadBlob(blob);
		//add the li element to the ordered list
		recordingsList.appendChild(li);
		
		
	}
	
	function registerServerListener(){
	
	$("#audioform").submit(function (event) {
		event.preventDefault();
	
		var formData = new FormData($(this)[0]);
	
		if (recordingBlob) {
			var recording = new Blob([recordingBlob], { type: "audio/wav" });
			formData.append("file", recording, "lastRecorded");
		}
		
		$.ajaxSetup({
			headers: {
				'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content')
			}
		});
	
		$.ajax({
			url: '/save-record',
			type: 'POST',
			cache : false,
			data : formData,
			processData: false,
			contentType: false,
			success: function(response) {
								$("#langresult p").text(response);
                            console.log('Successfully Uploaded Recorded Blob');
							},
            failure: function(response) { 
								console.log(response);
								alert(response); // error/failure
							}
			//etc
		});
	});
	}

	//helper function
	function __log(e, data) {
		log.innerHTML += "\n" + e + " " + (data || '');
	}
	})();