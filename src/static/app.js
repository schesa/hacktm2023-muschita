document.addEventListener("DOMContentLoaded", function () {
    var canvas = document.getElementById("renderCanvas");
    var engine = new BABYLON.Engine(canvas, true);

    // Create the scene
    var scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color3(0.8, 0.8, 0.8);

    // Create and position the camera
    var camera = new BABYLON.ArcRotateCamera(
        "camera",
        -Math.PI / 2,
        Math.PI / 2,
        4,
        new BABYLON.Vector3(0, 1, 0),
        scene
    );
    camera.attachControl(canvas, true);

    // Create a light source
    var light = new BABYLON.HemisphericLight(
        "light",
        new BABYLON.Vector3(0, 1, 0),
        scene
    );

    // Get the text parameter from the URL query string
    var urlParams = new URLSearchParams(window.location.search);
    var text = urlParams.get("text") || "Default Text";

    // Create a GUI plane for displaying the text
    var plane = BABYLON.MeshBuilder.CreatePlane("plane", { width: 2, height: 1 }, scene);
    plane.position.y = 1;
    plane.scaling.x = 0.5;

    // Create a dynamic texture for the GUI plane
    var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateForMesh(plane);

    // Create a GUI text control to display the text
    var textBlock = new BABYLON.GUI.TextBlock();
    textBlock.text = text;
    textBlock.color = "black";
    textBlock.fontSize = 48;
    textBlock.fontFamily = "Arial";
    textBlock.paddingTop = "20px";
    textBlock.paddingBottom = "20px";
    textBlock.paddingLeft = "40px";
    textBlock.paddingRight = "40px";

    // Add the text block to the advanced texture
    advancedTexture.addControl(textBlock);

    // Speech synthesis
    var utterance = new SpeechSynthesisUtterance();
    utterance.lang = "en-US";
    utterance.text = text;

    // Play the speech when the page loads
    speechSynthesis.speak(utterance);

    // Render the scene
    engine.runRenderLoop(function () {
        scene.render();
    });

    // Resize the canvas on window resize
    window.addEventListener("resize", function () {
        engine.resize();
    });
});
