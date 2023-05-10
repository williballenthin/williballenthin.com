importScripts("https://cdn.jsdelivr.net/pyodide/v0.23.2/full/pyodide.js");

async function main() {
    // pump log messages up to the main application,
    // so that they could be rendered to an element, etc.
    const _log = console.log;
    console.log = (...args) => {
        _log(...args);
        postMessage({
            "type": "log",
            "level": "log",
            "args": args,
        });
    };

    console.log("worker: loading pyodide");
    const pyodide = await loadPyodide();
 
    // install dependencies listed in requirements.txt.
    // this file must contain complete .whl URLs, not package version specs.
    {
        console.log("worker: loading micropip");
        await pyodide.loadPackage("micropip")
        const micropip = pyodide.pyimport("micropip");

        const requirements = await fetch("requirements.txt");
        for (const requirement of (await requirements.text()).split("\n")) {
            if (requirement === "") {
                continue;
            }
            if (requirement.indexOf("#") === 0) {
                continue;
            }
            console.log("worker: installing: ", requirement);
            await micropip.install(requirement);
        }
    }

    // initialize textual host environment,
    // providing the xterm.js driver and associated configuration.
    {
        const host = await(await fetch("textual_host.py")).text();
        pyodide.runPython(host);
    }

    // set __name__ == __pyodide__ so that the application can
    // detect this environment and configure and run itself.
    //
    // see the final lines of app.py.
    // this is a point of integration between js and python.
    {
        pyodide.globals.set("__name__", "__pyodide__");

        // transfer control to the textual application.
        {
            const app = await(await fetch("app.py")).text();

            console.log("worker: transferring control to Python app");
            const e = pyodide.runPython(app);
        }
    }
}

main();
