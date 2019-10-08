package JavaExtractor;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.concurrent.Callable;

import JavaExtractor.Common.MethodExtractor;
import com.github.javaparser.ast.body.MethodDeclaration;
import org.apache.commons.lang3.StringUtils;

import com.github.javaparser.ParseException;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.Common.Common;
import JavaExtractor.FeaturesEntities.ProgramFeatures;

public class ExtractFeaturesTask implements Callable<Void> {
	CommandLineValues m_CommandLineValues;
	Path filePath;
	MethodExtractor methodExtractor;

	public ExtractFeaturesTask(CommandLineValues commandLineValues, Path path) {
		m_CommandLineValues = commandLineValues;
		this.filePath = path;
		this.methodExtractor = new MethodExtractor();
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
		// write to a file thread safely
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
		String goodCode = null;
		String badCode = null;
		try {
			code = new String(Files.readAllBytes(this.filePath));
			LinkedHashMap<String, List<MethodDeclaration>> goodAndMutatedMethods = getGoodAndMutatedMethods(code);
			goodCode = methodDeclarationsToString(goodAndMutatedMethods.get("0"));
			badCode = methodDeclarationsToString(goodAndMutatedMethods.get("1"));
		} catch (IOException e) {
			e.printStackTrace();
			code = Common.EmptyString;
		}
		FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

		ArrayList<ProgramFeatures> features1 = featureExtractor.extractFeatures(goodCode);
		// Replace method names with 0 in features1;
		ArrayList<ProgramFeatures> features2 = featureExtractor.extractFeatures(badCode);
		// Replace method names with 1 in features2;

		features1.addAll(features2);

		return features1;
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

	private LinkedHashMap<String, List<MethodDeclaration>> getGoodAndMutatedMethods(String code) {

		List<MethodDeclaration> methods = methodExtractor.extractMethodsFromCode(code);
		List<MethodDeclaration> mutatedMethods = new ArrayList<>();
		for (MethodDeclaration method : methods) {
			mutatedMethods.add(methodExtractor.mutateMethod(method));
		}

		LinkedHashMap<String, List<MethodDeclaration>> methodsAndMutatedMethods = new LinkedHashMap<>();
		methodsAndMutatedMethods.put("0", methods);
		methodsAndMutatedMethods.put("1", mutatedMethods);

		return methodsAndMutatedMethods;
	}

	private String methodDeclarationsToString(List<MethodDeclaration> methodDeclarations) {
		StringWriter stringWriter = new StringWriter();
		PrintWriter writer = new PrintWriter(stringWriter, true);
		for (MethodDeclaration declaration : methodDeclarations) {
			writer.println(declaration);
		}
		return stringWriter.toString();
	}
}
