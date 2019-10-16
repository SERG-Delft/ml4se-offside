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
import java.util.stream.Stream;

import JavaExtractor.Common.MethodExtractor;
import JavaExtractor.Common.MethodMutator;
import com.github.javaparser.ast.body.MethodDeclaration;
import org.apache.commons.lang3.StringUtils;

import com.github.javaparser.ParseException;

import JavaExtractor.Common.CommandLineValues;
import JavaExtractor.Common.Common;
import JavaExtractor.FeaturesEntities.ProgramFeatures;

public class ExtractFeaturesTask implements Callable<Void> {
	private static final String GOOD_CODE_NAME = "0";
	private static final String BAD_CODE_NAME = "1";

	CommandLineValues m_CommandLineValues;
	Path filePath;
	MethodExtractor methodExtractor;
	MethodMutator methodMutator;

	public ExtractFeaturesTask(CommandLineValues commandLineValues, Path path) {
		m_CommandLineValues = commandLineValues;
		this.filePath = path;
		this.methodExtractor = new MethodExtractor();
		this.methodMutator = new MethodMutator();
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
			if (m_CommandLineValues.Evaluate){
				features = extractSingleFileForEvaluation();
			} else {
				features = extractSingleFileForTraining();
			}

		} catch (ParseException | IOException e) {
			e.printStackTrace();
			return;
		}
		if (features == null) {
			return;
		}

		String toPrint = featuresToString(features);
		// Caller of the JAR should handle writing to a file
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

	public ArrayList<ProgramFeatures> extractSingleFileForTraining() throws ParseException, IOException {
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

		ArrayList<ProgramFeatures> goodFeatures = featureExtractor.extractFeatures(goodCode);
		goodFeatures.forEach(programFeatures -> programFeatures.setName(GOOD_CODE_NAME));
		ArrayList<ProgramFeatures> badFeatures = featureExtractor.extractFeatures(badCode);
		badFeatures.forEach(programFeatures -> programFeatures.setName(BAD_CODE_NAME));

		ArrayList<ProgramFeatures> allFeatures = new ArrayList<>();
		Stream.of(goodFeatures, badFeatures).forEach(allFeatures::addAll);

		return allFeatures;
	}

	public ArrayList<ProgramFeatures> extractSingleFileForEvaluation() throws IOException, ParseException {
		String code = null;
		try {
			code = new String(Files.readAllBytes(this.filePath));
			List<MethodDeclaration> methods = methodExtractor.extractMethodsFromCode(code);
			FeatureExtractor featureExtractor = new FeatureExtractor(m_CommandLineValues);

			ArrayList<ProgramFeatures> features = featureExtractor.extractFeatures(methodDeclarationsToString(methods));
			features.forEach(programFeatures -> programFeatures.setName(this.filePath.toString() + ":" + programFeatures.getName()));

			return features;
		} catch (IOException e) {
			e.printStackTrace();
			code = Common.EmptyString;
		}

		return new ArrayList<>();
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
			mutatedMethods.add(methodMutator.mutateMethod(method));
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
