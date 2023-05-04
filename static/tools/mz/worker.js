importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.2/full/pyodide.js");

async function main() {
    console.log("hello from worker");

    const pyodide = await loadPyodide();

    await pyodide.loadPackage("micropip")
    const micropip = pyodide.pyimport("micropip");

    // install dependencies listed in requirements.txt.
    // this file must contain complete .whl URLs, not package version specs.
    const requirements = await fetch("requirements.txt");
    for (const requirement of (await requirements.text()).split("\n")) {
        console.log("installing: ", requirement);
        await micropip.install(requirement);
    }

    // initialize textual host environment,
    // providing the xterm.js driver and associated configuration.
    const host = await(await fetch("textual_host.py")).text();
    await pyodide.runPythonAsync(host);

    // define the application, making the class `__main__:FooApp` available.
    const app = await(await fetch("app.py")).text();
    await pyodide.runPythonAsync(app);

    console.log("running python app");
    // transfer control to the textual application.
    pyodide.runPython(`
        async def main():
            app = PEApp()
            await app.run_async()
        main()
    `);
}

main();