import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

export async function POST(req: NextRequest) {
  const brief = await req.json();

  // Write brief to temp file and call Python generator
  const briefJson = JSON.stringify(brief);
  const generatorPath = path.join(process.cwd(), "../../builder/website_generator.py");

  try {
    const tempBriefPath = `/tmp/brief_${Date.now()}.json`;
    await execAsync(`echo '${briefJson.replace(/'/g, "'\\''")}' > ${tempBriefPath}`);
    const { stdout } = await execAsync(`python3 ${generatorPath} ${tempBriefPath}`);

    // Extract the generated file path from stdout
    const match = stdout.match(/Website saved: (.+\.html)/);
    const htmlPath = match ? match[1].trim() : null;

    if (!htmlPath) {
      return NextResponse.json({ error: "Generation failed", stdout }, { status: 500 });
    }

    // Deploy to Netlify
    const deployPath = path.join(process.cwd(), "../../deploy/netlify_deploy.py");
    const { stdout: deployOut } = await execAsync(
      `python3 ${deployPath} "${htmlPath}" "${brief.business_name}"`
    );

    const urlMatch = deployOut.match(/Live: (https:\/\/[^\s]+)/);
    const url = urlMatch ? urlMatch[1] : null;

    return NextResponse.json({ success: true, url, htmlPath });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
