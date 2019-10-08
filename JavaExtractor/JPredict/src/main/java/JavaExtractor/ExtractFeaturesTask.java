package JavaExtractor;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;

import org.apache.commons.lang3.StringUtils;

import com.github.javaparser.ParseException;
import com.github.javaparser.ast.CompilationUnit;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.Common.Common;
import JavaExtractor.FeaturesEntities.ProgramFeatures;

public class ExtractFeaturesTask implements Callable<Void> {
	CommandLineValues m_CommandLineValues;
	Path filePath;

	public ExtractFeaturesTask(CommandLineValues commandLineValues, Path path) {
		m_CommandLineValues = commandLineValues;
		this.filePath = path;
	}

	public ExtractFeaturesTask(CommandLineValues commandLineValues) {
		m_CommandLineValues = commandLineValues;
	}

	@Override
	public Void call() throws Exception {
		//System.err.println("Extracting file: " + filePath);
		processFile();
		//System.err.println("Done with file: " + filePath);
		return null;
	}

	public void processFile() {
		ArrayList<ProgramFeatures> features;
		try {
			features = extractSingleFile();
		} catch (ParseException | IOException e) {
			e.printStackTrace();
			return;
		}
		if (features == null) {
			return;
		}

		String toPrint = featuresToString(features);
		if (toPrint.length() > 0) {
			System.out.println(toPrint);
		}
	}

	public void processCode() {
		String code = m_CommandLineValues.Code;

		ArrayList<ProgramFeatures> features;
		try {
			FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

			features = featureExtractor.extractFeatures(code);

			String toPrint = featuresToString(features);
			if (toPrint.length() > 0) {
				System.out.println(toPrint);
			}
		} catch (ParseException | IOException e) {
			e.printStackTrace();
			return;
		}
	}

	public ArrayList<ProgramFeatures> extractSingleFile() throws ParseException, IOException {
		String code = null;
		try {
			code = new String(Files.readAllBytes(this.filePath));
		} catch (IOException e) {
			e.printStackTrace();
			code = Common.EmptyString;
		}
		FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

		ArrayList<ProgramFeatures> features = featureExtractor.extractFeatures(code);

		return features;
	}

	public String featuresToString(ArrayList<ProgramFeatures> features) {
		if (features == null || features.isEmpty()) {
			return Common.EmptyString;
		}

		List<String> methodsOutputs = new ArrayList<>();

		for (ProgramFeatures singleMethodfeatures : features) {
			StringBuilder builder = new StringBuilder();

			String toPrint = Common.EmptyString;
			toPrint = singleMethodfeatures.toString();
			if (m_CommandLineValues.PrettyPrint) {
				toPrint = toPrint.replace(" ", "\n\t");
			}
			builder.append(toPrint);


			methodsOutputs.add(builder.toString());

		}
		return StringUtils.join(methodsOutputs, "\n");
	}
}
