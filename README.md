# BloomDepth 3D Flowers 1.0.0

Minecraft Java 26.3 · Fabric Loader 0.19.5+ · Java 25 · Client + Server.

BloomDepth replaces the models of 29 vanilla flowers and flowering plants in the world and in the inventory. It covers 17 small flowers, the five tall flowers, pink petals, wildflowers, cactus flower, spore blossom, flowering azalea, mangrove propagule and chorus flower. It includes both states of eyeblossom, live and dead chorus flowers, and growing torchflower and pitcher plants.

The 19 potted plants retain their vanilla pot geometry. ColoredM 1.0.1's 16 pot colors inherit the new geometry for all 19 plants. Existing worlds use vanilla block and item IDs.

For singleplayer, install the JAR in the client's `mods` folder. For multiplayer, put the same JAR on the server and every player's client. ColoredM is optional. BloomDepth itself requires Fabric Loader. Install Fabric API 0.163.0+ for 26.3 when playing with CivicCraft or ColoredM.

The models and textures are included in `src/main/resources`. To rebuild from source, use JDK 25 and run `gradlew.bat build` on Windows or `bash gradlew build` on Linux. To regenerate the assets, install Pillow and run `python tools/generate_resources.py path/to/minecraft-26.3-client.jar`.

Run `python tools/draw_icon.py --curseforge BloomDepth-icon.png` with Pillow to regenerate the embedded icon and a 512px project logo.

License MIT. Created with ChatGPT by OpenAI.
